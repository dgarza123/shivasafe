import os
import shutil

SOURCE_PATH = "your/path/to/yamls.zip"  # ← Update this path
DEST_DIR = "upload"
DEST_PATH = os.path.join(DEST_DIR, "yamls.zip")

def upload_zip():
    if not os.path.exists(SOURCE_PATH):
        print(f"[✘] Source file not found: {SOURCE_PATH}")
        return

    os.makedirs(DEST_DIR, exist_ok=True)
    shutil.copy(SOURCE_PATH, DEST_PATH)
    print(f"[✔] Copied {SOURCE_PATH} → {DEST_PATH}")

if __name__ == "__main__":
    upload_zip()
