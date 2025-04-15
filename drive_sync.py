import os
from google_drive_manager import list_drive_files, download_drive_file

EVIDENCE_DIR = "evidence"

def sync_drive_to_evidence():
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    files = list_drive_files()
    downloaded = []

    for f in files:
        name = f["name"]
        ext = os.path.splitext(name)[1].lower()

        if ext not in [".yaml", ".pdf"]:
            continue

        dest_path = os.path.join(EVIDENCE_DIR, name)

        # Skip if already present
        if os.path.exists(dest_path):
            continue

        try:
            download_drive_file(f["id"], dest_path)
            downloaded.append(name)
        except Exception as e:
            print(f"[sync] Failed to download {name}: {e}")

    return downloaded