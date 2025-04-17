import os
import zipfile
import sqlite3
import yaml
from glob import glob

DB_PATH = "data/hawaii.db"
UPLOAD_DIR = "uploads"
EXTRACT_DIR = os.path.join(UPLOAD_DIR, "extracted")

def parse_yaml_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("transactions", []), data.get("sha256"), data.get("document")

def infer_status(parcel_id):
    if not parcel_id or parcel_id.strip() in ["", "None"]:
        return "Unknown"
    if parcel_id.startswith("TMK") or ":" in parcel_id:
        return "Public"
    return "Unknown"

def normalize_amount(value):
    if not value:
        return None
    return str(value).replace("$", "").replace(",", "").strip()

def build_database_from_zip(zip_path):
    # Step 1: Cleanup
    if os.path.exists(EXTRACT_DIR):
        for f in glob(f"{EXTRACT_DIR}/*"):
            os.remove(f)
    else:
        os.makedirs(EXTRACT_DIR, exist_ok=True)

    # Step 2: Extract zip
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)

    # Step 3: Parse and insert
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS parcels")
    c.execute("""
        CREATE TABLE parcels (
            certificate_id TEXT,
            grantor TEXT,
            grantee TEXT,
            amount TEXT,
            parcel_id TEXT,
            parcel_valid BOOLEAN,
            registry_key TEXT,
            escrow_id TEXT,
            cert_id TEXT,
            date_signed TEXT,
            transfer_bank TEXT,
            country TEXT,
            link TEXT,
            sha256 TEXT,
            filename TEXT,
            status TEXT
        )
    """)

    count = 0
    for yaml_path in glob(f"{EXTRACT_DIR}/*.yaml"):
        rows, sha, filename = parse_yaml_file(yaml_path)
        for row in rows:
            row["status"] = infer_status(row.get("parcel_id"))
            values = (
                row.get("certificate_id"),
                row.get("grantor"),
                row.get("grantee"),
                normalize_amount(row.get("amount")),
                row.get("parcel_id"),
                row.get("parcel_valid", False),
                row.get("registry_key"),
                row.get("escrow_id"),
                row.get("cert_id"),
                row.get("date_signed"),
                row.get("transfer_bank"),
                row.get("country"),
                row.get("link"),
                sha,
                filename,
                row.get("status")
            )
            c.execute("INSERT INTO parcels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
            count += 1

    conn.commit()
    conn.close()
    return count, DB_PATH
