import os
import streamlit as st
from google_drive_manager import list_drive_files, download_drive_file

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def sync_drive_to_local():
    """
    Downloads all YAML and PDF files from Drive into /evidence/.
    """
    synced_files = []
    drive_files = list_drive_files()

    for file in drive_files:
        name = file.get("name", "")
        file_id = file.get("id")

        if name.endswith(".yaml") or name.endswith(".pdf"):
            local_path = os.path.join(EVIDENCE_DIR, name)

            # Skip if file already exists
            if os.path.exists(local_path):
                continue

            try:
                download_drive_file(file_id, local_path)
                synced_files.append(name)
            except Exception as e:
                print(f"[sync] Failed to download {name}: {e}")

    return synced_files
