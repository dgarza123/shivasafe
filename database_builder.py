# database_builder.py

import os
import sqlite3
import yaml

def parse_yaml(yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    rows = []
    for tx in data.get("transactions", []):
        row = {
            "certificate_id": data.get("certificate_id", ""),
            "sha256": data.get("sha256", ""),
            "parcel_id": tx.get("parcel_id", ""),
            "grantee": tx.get("grantee", ""),
            "grantor": tx.get("grantor", ""),
            "amount": tx.get("amount", ""),
            "country": tx.get("country", ""),
            "registry_key": tx.get("registry_key", ""),
            "escrow_id": tx.get("escrow_id", ""),
            "status": "Unknown" if tx.get("parcel_valid") is None else ("Public" if tx["parcel_valid"] else "Disappeared"),
            "latitude": tx.get("latitude", None),
            "longitude": tx.get("longitude", None),
        }
        rows.append(row)
    return rows

def build_database_from_folder(folder_path, output_path="data/hawaii.db"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    conn = sqlite3.connect(output_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS parcels")
    c.execute("""
        CREATE TABLE parcels (
            certificate_id TEXT,
            sha256 TEXT,
            parcel_id TEXT,
            grantee TEXT,
            grantor TEXT,
            amount TEXT,
            country TEXT,
            registry_key TEXT,
            escrow_id TEXT,
            status TEXT,
            latitude REAL,
            longitude REAL
        )
    """)

    total_rows = 0
    for root, _, files in os.walk(folder_path):
        for fname in files:
            if fname.endswith(".yaml") or fname.endswith(".yml"):
                full_path = os.path.join(root, fname)
                rows = parse_yaml(full_path)
                for row in rows:
                    c.execute("""
                        INSERT INTO parcels (
                            certificate_id, sha256, parcel_id, grantee, grantor,
                            amount, country, registry_key, escrow_id, status,
                            latitude, longitude
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(row.values()))
                    total_rows += 1

    conn.commit()
    conn.close()
    return total_rows, output_path
