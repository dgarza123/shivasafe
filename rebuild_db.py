# rebuild_db.py

import os
import sqlite3
import yaml
import glob

def build_db(yaml_folder="data"):
    os.makedirs("data", exist_ok=True)
    db_path = "data/hawaii.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS parcels")
    c.execute("""
        CREATE TABLE parcels (
            certificate_id TEXT,
            parcel_id TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT,
            grantee TEXT,
            amount TEXT
        )
    """)

    total = 0
    for f in glob.glob(os.path.join(yaml_folder, "*.yaml")):
        with open(f, "r") as file:
            yml = yaml.safe_load(file)

        cert_id = os.path.basename(f).replace("_entities.yaml", "")
        transactions = yml.get("transactions", [])
        for tx in transactions:
            c.execute("""
                INSERT INTO parcels (certificate_id, parcel_id, latitude, longitude, status, grantee, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cert_id,
                tx.get("parcel_id", ""),
                tx.get("latitude"),
                tx.get("longitude"),
                tx.get("status", ""),
                tx.get("grantee", ""),
                tx.get("amount", "")
            ))
            total += 1

    conn.commit()
    conn.close()
    return total
