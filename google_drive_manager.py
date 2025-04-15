import os
import mimetypes
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ✅ Load credentials from Streamlit secrets or JSON file
def get_drive_service():
    if "gdrive" in os.environ:
        import streamlit as st
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gdrive"],
            scopes=["https://www.googleapis.com/auth/drive"]
        )
    else:
        credentials = service_account.Credentials.from_service_account_file(
            "shiva-pdf-f5d0f5a2a433.json",
            scopes=["https://www.googleapis.com/auth/drive"]
        )
    return build("drive", "v3", credentials=credentials)

# ✅ Define your destination folder ID
DRIVE_FOLDER_ID = "1Cxhy9WstQ5-XWHx9ZtVXLHaZqBGHbs5n"  # Your actual Drive folder

# ✅ Upload a file to Google Drive
def upload_to_drive(filepath: str) -> str:
    service = get_drive_service()
    filename = os.path.basename(filepath)
    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    file_metadata = {
        "name": filename,
        "parents": [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(filepath, mimetype=mime_type, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return uploaded_file.get("id")
