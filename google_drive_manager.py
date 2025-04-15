import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

SERVICE_ACCOUNT_FILE = "shiva-pdf-80b3c5254af7.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = "1Cxhy9WstQ5-XWHx9ZtVXLHaZqBGHbs5n"  # ShivaSafe evidence folder

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

def upload_to_drive(local_path, remote_filename=None):
    file_metadata = {
        "name": remote_filename or os.path.basename(local_path),
        "parents": [FOLDER_ID]
    }
    media = MediaIoBaseUpload(open(local_path, "rb"), mimetype="application/octet-stream")
    uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return uploaded.get("id")

def list_drive_files():
    query = f"'{FOLDER_ID}' in parents and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name, mimeType, modifiedTime)").execute()
    return results.get("files", [])

def download_drive_file(file_id, save_as):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(save_as, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return save_as
