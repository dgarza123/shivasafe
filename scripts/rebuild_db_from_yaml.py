# rebuild_db_from_yaml.py

import os
import yaml
import sqlite3

DB_PATH = "data/hawaii.db"
TABLE_NAME = "parcels"

# Ensure target directory exists
os.makedirs("data", exist_ok=True)

# Create database schema
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

# Parse a single YAML file
def parse_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

# Normalize parcel status
def infer_status(entry):
    if not entry.get("parcel_valid"):
        return "Disappeared"
    return "Public"

# Build database from YAML directory
def build_database_from_folder(folder):
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    inserted = 0
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".yaml"):
                full_path = os.path.join(root, file)
                data = parse_yaml(full_path)

                sha = data.get("sha256", "")
                filename = data.get("document", "")
                cert = os.path.splitext(os.path.basename(full_path))[0]

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
                        bool(tx.get("parcel_valid")),
                        tx.get("registry_key"),
                        tx.get("escrow_id"),
                        tx.get("transfer_bank"),
                        tx.get("country"),
                        tx.get("date_signed"),
                        infer_status(tx)
                    ))
                    inserted += 1

    conn.commit()
    conn.close()
    return inserted

if __name__ == "__main__":
    folder = "yamls"  # change this path if needed
    count = build_database_from_folder(folder)
    print(f"✅ Built {DB_PATH} with {count} transactions.")
