import os
import sqlite3
import yaml
import hashlib
import glob

def parse_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def infer_status(parcel_id, valid_tmk_list):
    if not parcel_id:
        return "Unknown"
    if parcel_id in valid_tmk_list:
        return "Public"
    return "Disappeared"

def build_database_from_zip_extract(folder_path, tmk_csv_path=None):
    db_path = "data/hawaii.db"
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create table
    c.execute("""
        CREATE TABLE IF NOT EXISTS parcels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sha256 TEXT,
            document TEXT,
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
            status TEXT
        )
    """)

    # Load optional TMK list if provided
    valid_tmk = set()
    if tmk_csv_path and os.path.exists(tmk_csv_path):
        import pandas as pd
        df = pd.read_csv(tmk_csv_path)
        valid_tmk = set(df["parcel_id"].astype(str).str.strip())

    # Parse YAML files
    count = 0
    for file in glob.glob(os.path.join(folder_path, "*.yaml")):
        ydata = parse_yaml(file)
        sha256 = ydata.get("sha256", "")
        document = ydata.get("document", "")
        txs = ydata.get("transactions", [])
        for tx in txs:
            parcel_id = tx.get("parcel_id")
            status = infer_status(parcel_id, valid_tmk)

            row = (
                sha256,
                document,
                tx.get("grantor"),
                tx.get("grantee"),
                tx.get("amount"),
                parcel_id,
                tx.get("parcel_valid", False),
                tx.get("registry_key"),
                tx.get("escrow_id"),
                tx.get("cert_id"),
                tx.get("date_signed"),
                tx.get("transfer_bank"),
                tx.get("country"),
                tx.get("link"),
                status,
            )

            c.execute("""
                INSERT INTO parcels (
                    sha256, document, grantor, grantee, amount, parcel_id, parcel_valid,
                    registry_key, escrow_id, cert_id, date_signed, transfer_bank,
                    country, link, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)
            count += 1

    conn.commit()
    conn.close()
    return count, db_path
