# database_builder.py
import os
import yaml
import sqlite3
import pandas as pd

def extract_transactions(yaml_path):
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    sha256 = data.get("sha256", "")
    document = data.get("document", "")

    transactions = data.get("transactions", [])
    results = []
    for tx in transactions:
        results.append({
            "certificate_id": tx.get("cert_id", ""),
            "parcel_id": tx.get("parcel_id", ""),
            "amount": tx.get("amount", ""),
            "grantee": tx.get("grantee", ""),
            "grantor": tx.get("grantor", ""),
            "registry_key": tx.get("registry_key", ""),
            "escrow_id": tx.get("escrow_id", ""),
            "country": tx.get("country", ""),
            "transfer_bank": tx.get("transfer_bank", ""),
            "status": tx.get("status", "Unknown"),
            "latitude": tx.get("latitude", None),
            "longitude": tx.get("longitude", None),
            "sha256": sha256,
            "document": document,
            "link": tx.get("link", ""),
            "date_signed": tx.get("date_signed", "")
        })
    return results

def build_database_from_zip(zip_folder):
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
            registry_key TEXT,
            escrow_id TEXT,
            country TEXT,
            transfer_bank TEXT,
            status TEXT,
            latitude REAL,
            longitude REAL,
            sha256 TEXT,
            document TEXT,
            link TEXT,
            date_signed TEXT
        )
    """)

    all_records = []
    for root, _, files in os.walk(zip_folder):
        for file in files:
            if file.endswith(".yaml"):
                try:
                    records = extract_transactions(os.path.join(root, file))
                    all_records.extend(records)
                except Exception as e:
                    print(f"⚠️ Failed to parse {file}: {e}")

    df = pd.DataFrame(all_records)
    df.to_sql("parcels", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    return len(df), db_path
