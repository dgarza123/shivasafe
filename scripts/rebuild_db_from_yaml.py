# scripts/rebuild_db_from_yaml.py

import os
import yaml
import sqlite3

DB_PATH = "data/hawaii.db"
TABLE_NAME = "parcels"
SOURCE_FOLDER = "evidence"

def create_table(conn):
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            certificate_id TEXT,
            sha256 TEXT,
            filename TEXT,
            grantor TEXT,
            grantee TEXT,
            amount TEXT,
            parcel_id TEXT,
            parcel_valid BOOLEAN,
            registry_key TEXT,
            escrow_id TEXT,
            transfer_bank TEXT,
            country TEXT,
            date_signed TEXT,
            status TEXT
        )
    """)
    conn.commit()

def parse_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def infer_status(entry):
    if not entry.get("parcel_valid", True):
        return "Disappeared"
    return "Public"

def build_db():
    if not os.path.exists(SOURCE_FOLDER):
        raise FileNotFoundError(f"YAML source folder not found: {SOURCE_FOLDER}")

    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    inserted = 0
    for root, _, files in os.walk(SOURCE_FOLDER):
        for file in files:
            if file.endswith(".yaml"):
                full_path = os.path.join(root, file)
                try:
                    data = parse_yaml(full_path)
                    sha = data.get("sha256", "")
                    filename = data.get("document", "")
                    cert = data.get("certificate_number") or os.path.splitext(file)[0]

                    for tx in data.get("transactions", []):
                        conn.execute(f"""
                            INSERT INTO {TABLE_NAME} (
                                certificate_id, sha256, filename, grantor, grantee,
                                amount, parcel_id, parcel_valid, registry_key,
                                escrow_id, transfer_bank, country, date_signed, status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            cert,
                            sha,
                            filename,
                            tx.get("grantor"),
                            tx.get("grantee"),
                            tx.get("amount"),
                            tx.get("parcel_id"),
                            bool(tx.get("parcel_valid", True)),
                            tx.get("registry_key"),
                            tx.get("escrow_id"),
                            tx.get("transfer_bank"),
                            tx.get("country"),
                            tx.get("date_signed"),
                            infer_status(tx)
                        ))
                        inserted += 1
                except Exception as e:
                    print(f"⚠️ Failed to process {file}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Built {DB_PATH} with {inserted} transactions.")
    return inserted
