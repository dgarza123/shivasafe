import os
import sqlite3
import yaml
import zipfile

EVIDENCE_DIR = "evidence"
DB_PATH = "Hawaii.db"
ZIP_PATH = "Hawaii Yamls (4).zip"  # Update with your actual uploaded zip filename

def unzip_yamls():
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EVIDENCE_DIR)
    print("✅ YAML files unzipped to evidence/")

def create_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            tmk TEXT,
            certificate TEXT,
            yaml_file TEXT
        )
    """)
    conn.commit()
    conn.close()

def ingest_yaml_files():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for fname in os.listdir(EVIDENCE_DIR):
        if not fname.endswith("_entities.yaml"):
            continue
        path = os.path.join(EVIDENCE_DIR, fname)
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        cert = fname.replace("_entities.yaml", "")
        for tx in data.get("transactions", []):
            tmk = str(tx.get("parcel_id", "")).strip()
            if tmk:
                c.execute("INSERT INTO transactions (tmk, certificate, yaml_file) VALUES (?, ?, ?)",
                          (tmk, cert, fname))
    conn.commit()
    conn.close()
    print("✅ YAML records ingested into Hawaii.db")

if __name__ == "__main__":
    unzip_yamls()
    create_table()
    ingest_yaml_files()
