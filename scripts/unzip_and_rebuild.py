import os
import zipfile
import shutil
import sys

# Ensure root is in sys.path so Streamlit can find local modules
sys.path.append(os.path.abspath("."))

from scripts.rebuild_db_from_yaml import build_db

EVIDENCE_DIR = "evidence"
ZIP_FILE = "upload/yamls.zip"

def unzip_yaml_bundle(zip_path, extract_to=EVIDENCE_DIR):
    if not os.path.exists(zip_path):
        print(f"[✘] Zip file not found: {zip_path}")
        return

    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    # Move nested .yaml files to /evidence/
    for root, _, files in os.walk(extract_to):
        for f in files:
            if f.endswith(".yaml"):
                src = os.path.join(root, f)
                dst = os.path.join(extract_to, f)
                if src != dst:
                    shutil.move(src, dst)

    print("[✔] YAML files extracted to /evidence/")
    build_db()

if __name__ == "__main__":
    unzip_yaml_bundle(ZIP_FILE)
