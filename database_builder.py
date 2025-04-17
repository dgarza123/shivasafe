# database_builder.py

import os
import yaml
import sqlite3

def parse_yaml_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    transactions = data.get("transactions", [])
    parsed = []
    for tx in transactions:
        parsed.append({
            "certificate_id": data.get("certificate_id", "Unknown"),
            "sha256": data.get("sha256", ""),
            "parcel_id": tx.get("parcel_id", ""),
            "parcel_valid": tx.get("parcel_valid", False),
            "grantee": tx.get("grantee", ""),
            "grantor": tx.get("grantor", ""),
            "amount": tx.get("amount", ""),
            "registry_key": tx.get("registry_key", ""),
            "escrow_id": tx.get("escrow_id", ""),
            "transfer_bank": tx.get("transfer_bank", ""),
            "country": tx.get("country", ""),
            "status": tx.get("status", "Public"),
            "latitude": tx.get("latitude", None),
            "longitude": tx.get("longitude", None),
            "link": tx.get("link", "")
        })
    return parsed

def build_database_from_folder(folder_path):
    db_path = "data/hawaii.db"
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create parcels table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parcels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT,
            sha256 TEXT,
            parcel_id TEXT,
            parcel_valid BOOLEAN,
            grantee TEXT,
            grantor TEXT,
            amount TEXT,
            registry_key TEXT,
            escrow_id TEXT,
            transfer_bank TEXT,
            country TEXT,
            status TEXT,
            latitude REAL,
            longitude REAL,
            link TEXT
        )
    """)

    conn.commit()

    # Scan all .yaml files
    count = 0
    for root, _, files in os.walk(folder_path):
        for fname in files:
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                try:
                    path = os.path.join(root, fname)
                    rows = parse_yaml_file(path)
                    for row in rows:
                        values = tuple(row.get(k) for k in [
                            "certificate_id", "sha256", "parcel_id", "parcel_valid", "grantee",
                            "grantor", "amount", "registry_key", "escrow_id", "transfer_bank",
                            "country", "status", "latitude", "longitude", "link"
                        ])
                        cursor.execute("""
                            INSERT INTO parcels (
                                certificate_id, sha256, parcel_id, parcel_valid, grantee,
                                grantor, amount, registry_key, escrow_id, transfer_bank,
                                country, status, latitude, longitude, link
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, values)
                        count += 1
                except Exception as e:
                    print(f"[!] Failed to parse {fname}: {e}")

    conn.commit()
    conn.close()

    return count, db_path
