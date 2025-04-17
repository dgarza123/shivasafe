# rebuild_db.py

import os
import sqlite3
import yaml

def build_db(yaml_folder: str, db_path: str = "data/hawaii.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parcels (
            certificate_id TEXT,
            document TEXT,
            sha256 TEXT,
            parcel_id TEXT,
            parcel_valid BOOLEAN,
            grantor TEXT,
            grantee TEXT,
            amount TEXT,
            escrow_id TEXT,
            registry_key TEXT,
            transfer_bank TEXT,
            country TEXT,
            link TEXT,
            date_signed TEXT,
            status TEXT DEFAULT 'Public'
        )
    """)

    inserted = 0

    for filename in os.listdir(yaml_folder):
        if not filename.endswith(".yaml"):
            continue

        path = os.path.join(yaml_folder, filename)
        with open(path, "r") as f:
            try:
                y = yaml.safe_load(f)
                sha = y.get("sha256", "")
                doc = y.get("document", "")
                cert_id = y.get("certificate_id", os.path.splitext(filename)[0])
                transactions = y.get("transactions", [])

                for tx in transactions:
                    cursor.execute("""
                        INSERT INTO parcels (
                            certificate_id, document, sha256,
                            parcel_id, parcel_valid, grantor, grantee,
                            amount, escrow_id, registry_key,
                            transfer_bank, country, link, date_signed, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        cert_id, doc, sha,
                        tx.get("parcel_id"),
                        bool(tx.get("parcel_valid", True)),
                        tx.get("grantor"),
                        tx.get("grantee"),
                        tx.get("amount"),
                        tx.get("escrow_id"),
                        tx.get("registry_key"),
                        tx.get("transfer_bank"),
                        tx.get("country"),
                        tx.get("link"),
                        tx.get("date_signed"),
                        tx.get("status", "Public")
                    ))
                    inserted += 1

            except Exception as e:
                print(f"⚠️ Skipping {filename}: {e}")

    conn.commit()
    conn.close()
    return inserted, db_path
