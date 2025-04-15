import os
import io
import mimetypes
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# ✅ Your verified Google Drive folder
DRIVE_FOLDER_ID = "1Cxhy9WstQ5-XWHx9ZtVXLHaZqBGHbs5n"

# ✅ Initialize Google Drive service
def get_drive_service():
    try:
        import streamlit as st
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gdrive"],
            scopes=["https://www.googleapis.com/auth/drive"]
        )
    except Exception:
        credentials = service_account.Credentials.from_service_account_file(
            "shiva-pdf-f5d0f5a2a433.json",
            scopes=["https://www.googleapis.com/auth/drive"]
        )
    return build("drive", "v3", credentials=credentials)

# ✅ Upload file to Drive folder
def upload_to_drive(filepath: str) -> str:
    service = get_drive_service()
    filename = os.path.basename(filepath)
    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    file_metadata = {
        "name": filename,
        "parents": [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(filepath, mimetype=mime_type, resumable=True)
    uploaded_file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    return uploaded_file.get("id")

# ✅ List all files in Drive folder
def list_drive_files():
    service = get_drive_service()
    results = service.files().list(
        q=f"'{DRIVE_FOLDER_ID}' in parents and trashed=false",
        fields="files(id, name, mimeType, createdTime, modifiedTime)"
    ).execute()
    return results.get("files", [])

# ✅ Download file from Drive
def download_drive_file(file_id, destination_path):
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
