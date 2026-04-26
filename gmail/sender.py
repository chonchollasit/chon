import base64
import re
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from drive.uploader import get_creds


def _get_gmail_service():
    creds = get_creds()
    return build("gmail", "v1", credentials=creds)


def send_email(to: str, subject: str, body: str):
    service = _get_gmail_service()
    message = MIMEText(body, "plain", "utf-8")
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print(f"[Gmail] Email sent to {to}: {subject}")
