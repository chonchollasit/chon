import io
import os
import httplib2
import google_auth_httplib2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import requests

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://mail.google.com/",
]
RESEARCHER_FOLDER_NAME = "Researcher"
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"


def _bootstrap_credential_files():
    """Write credentials from env vars to files if files are missing."""
    if not os.path.exists(CREDENTIALS_PATH):
        raw = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
        if raw:
            with open(CREDENTIALS_PATH, "w") as f:
                f.write(raw)
    if not os.path.exists(TOKEN_PATH):
        raw = os.environ.get("GOOGLE_TOKEN_JSON", "")
        if raw:
            with open(TOKEN_PATH, "w") as f:
                f.write(raw)


def _get_creds():
    _bootstrap_credential_files()
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            session = requests.Session()
            session.verify = False
            creds.refresh(Request(session=session))
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())
    return creds


def _get_drive_service():
    creds = _get_creds()
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=http)
    return build("drive", "v3", http=authorized_http)


def get_creds():
    return _get_creds()


def _get_or_create_researcher_folder(service) -> str:
    query = (
        f"name='{RESEARCHER_FOLDER_NAME}' "
        "and mimeType='application/vnd.google-apps.folder' "
        "and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])

    if folders:
        folder_id = folders[0]["id"]
        print(f"[Drive] Found existing folder '{RESEARCHER_FOLDER_NAME}' (id={folder_id})")
        return folder_id

    folder_metadata = {
        "name": RESEARCHER_FOLDER_NAME,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    folder_id = folder["id"]
    print(f"[Drive] Created folder '{RESEARCHER_FOLDER_NAME}' (id={folder_id})")
    return folder_id


def _upload_file(service, file_path: str, folder_id: str) -> tuple[str, str]:
    filename = os.path.basename(file_path)
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(
        file_path,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )
    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id, name, webViewLink")
        .execute()
    )
    link = uploaded.get("webViewLink", f"https://drive.google.com/file/d/{uploaded['id']}/view")
    print(f"[Drive] Uploaded '{uploaded['name']}' -> {link}")
    return uploaded["id"], link


def upload_to_researcher_folder(file_path: str) -> tuple[str, str]:
    """Upload a new file to the Researcher folder. Returns (file_id, web_view_link)."""
    service = _get_drive_service()
    folder_id = _get_or_create_researcher_folder(service)
    return _upload_file(service, file_path, folder_id)


def upload_to_folder(file_path: str, folder_id: str) -> tuple[str, str]:
    """Upload a new file to a specific folder ID. Returns (file_id, web_view_link)."""
    service = _get_drive_service()
    return _upload_file(service, file_path, folder_id)


def update_file_in_drive(file_id: str, file_path: str) -> str:
    """Overwrite an existing Drive file in-place. Returns updated web_view_link."""
    service = _get_drive_service()
    media = MediaFileUpload(
        file_path,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        resumable=True,
    )
    updated = (
        service.files()
        .update(fileId=file_id, media_body=media, fields="id, name, webViewLink")
        .execute()
    )
    link = updated.get("webViewLink", f"https://drive.google.com/file/d/{updated['id']}/view")
    print(f"[Drive] Updated '{updated['name']}' -> {link}")
    return link


def list_files_in_folder(folder_id: str, max_results: int = 10) -> list[dict]:
    """List files in a folder sorted by creation time descending."""
    service = _get_drive_service()
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        orderBy="createdTime desc",
        pageSize=max_results,
        fields="files(id, name, createdTime, mimeType)",
    ).execute()
    return results.get("files", [])


def download_file_from_drive(file_id: str) -> bytes:
    """Download a file's raw bytes from Drive."""
    service = _get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return fh.read()
