# database_builder.py
import os
import sqlite3
import zipfile
import yaml
import shutil

def parse_yaml_file(path):
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except:
        return None

def build_database_from_zip(zip_path):
    extract_path = "uploads/extracted"
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    return build_database_from_folder(extract_path)

def build_database_from_folder(folder):
    db_path = "data/hawaii.db"
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS parcels")
    cursor.execute("""
        CREATE TABLE parcels (
            certificate_id TEXT,
            parcel_id TEXT,
            amount TEXT,
            grantee TEXT,
            grantor TEXT,
            country TEXT,
            transfer_bank TEXT,
            escrow_id TEXT,
            registry_key TEXT,
            date_signed TEXT,
            status TEXT,
            latitude REAL,
            longitude REAL
        )
    """)

    count = 0
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                full_path = os.path.join(root, file)
                data = parse_yaml_file(full_path)
                if not data:
                    continue
                txs = data.get("transactions", [])
                for tx in txs:
                    row = (
                        tx.get("cert_id"),
                        tx.get("parcel_id"),
                        tx.get("amount"),
                        tx.get("grantee"),
                        tx.get("grantor"),
                        tx.get("country"),
                        tx.get("transfer_bank"),
                        tx.get("escrow_id"),
                        tx.get("registry_key"),
                        tx.get("date_signed"),
                        tx.get("status", "Public"),
                        tx.get("latitude"),
                        tx.get("longitude")
                    )
                    cursor.execute("""
                        INSERT INTO parcels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, row)
                    count += 1

    conn.commit()
    conn.close()
    return count, db_path
