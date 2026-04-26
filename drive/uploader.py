import os
import httplib2
import google_auth_httplib2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import requests

SCOPES = ["https://www.googleapis.com/auth/drive"]
RESEARCHER_FOLDER_NAME = "Researcher"
TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"


def _get_drive_service():
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
    http = httplib2.Http(disable_ssl_certificate_validation=True)
    authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=http)
    return build("drive", "v3", http=authorized_http)


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


def upload_to_researcher_folder(file_path: str) -> str:
    service = _get_drive_service()
    folder_id = _get_or_create_researcher_folder(service)

    filename = os.path.basename(file_path)
    file_metadata = {
        "name": filename,
        "parents": [folder_id],
    }
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
    print(
        f"[Drive] Uploaded '{uploaded['name']}' -> {uploaded.get('webViewLink', 'n/a')}"
    )
    return uploaded["id"]
