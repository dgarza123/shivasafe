# rebuild_db.py

import sqlite3
import yaml
import os

def build_db(yaml_folder, db_path="data/hawaii.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS parcels")
    c.execute("""
        CREATE TABLE parcels (
            certificate_id TEXT,
            parcel_id TEXT,
            registry_key TEXT,
            escrow_id TEXT,
            grantor TEXT,
            grantee TEXT,
            amount TEXT,
            date_signed TEXT,
            transfer_bank TEXT,
            country TEXT,
            status TEXT,
            link TEXT
        )
    """)

    inserted = 0

    for fname in os.listdir(yaml_folder):
        if not fname.endswith(".yaml"):
            continue
        fpath = os.path.join(yaml_folder, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            ydata = yaml.safe_load(f)

        for tx in ydata.get("transactions", []):
            values = (
                ydata.get("certificate_id", ""),
                tx.get("parcel_id", ""),
                tx.get("registry_key", ""),
                tx.get("escrow_id", ""),
                tx.get("grantor", ""),
                tx.get("grantee", ""),
                tx.get("amount", ""),
                tx.get("date_signed", ""),
                tx.get("transfer_bank", ""),
                tx.get("country", ""),
                tx.get("status", ""),
                tx.get("link", "")
            )
            c.execute("INSERT INTO parcels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
            inserted += 1

    conn.commit()
    conn.close()
    return inserted
