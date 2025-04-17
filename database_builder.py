# database_builder.py

import os
import sqlite3
import yaml
import csv

def build_database_from_folder(folder_path):
    db_path = "data/hawaii.db"
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop existing table if exists
    cursor.execute("DROP TABLE IF EXISTS parcels")

    # Create new schema with status column
    cursor.execute("""
        CREATE TABLE parcels (
            parcel_id TEXT,
            certificate_id TEXT,
            latitude REAL,
            longitude REAL,
            grantee TEXT,
            amount TEXT,
            status TEXT
        )
    """)

    count = 0

    # Load all YAML files
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".yaml"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    try:
                        data = yaml.safe_load(f)
                        if not data:
                            continue
                        cert_id = os.path.splitext(file)[0].replace("_entities", "")

                        for txn in data.get("transactions", []):
                            parcel = txn.get("parcel_id")
                            grantee = txn.get("grantee")
                            amount = txn.get("amount")
                            lat = txn.get("latitude", None)
                            lon = txn.get("longitude", None)
                            status = txn.get("status", "Unknown")

                            cursor.execute("""
                                INSERT INTO parcels (parcel_id, certificate_id, latitude, longitude, grantee, amount, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (parcel, cert_id, lat, lon, grantee, amount, status))
                            count += 1
                    except Exception as e:
                        print(f"Failed to process {file}: {e}")

    conn.commit()
    conn.close()
    return count, db_path
