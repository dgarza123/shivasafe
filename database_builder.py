# database_builder.py
import os
import sqlite3
import yaml

def parse_transaction_file(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    txns = []
    for tx in data.get("transactions", []):
        txns.append({
            "certificate_id": data.get("document", ""),
            "parcel_id": tx.get("parcel_id", "").strip(),
            "latitude": tx.get("latitude"),
            "longitude": tx.get("longitude"),
            "grantee": tx.get("grantee", ""),
            "grantor": tx.get("grantor", ""),
            "amount": tx.get("amount", ""),
            "registry_key": tx.get("registry_key", ""),
            "escrow_id": tx.get("escrow_id", ""),
            "transfer_bank": tx.get("transfer_bank", ""),
            "country": tx.get("country", ""),
            "status": "Public" if tx.get("parcel_valid") else "Disappeared",
        })
    return txns

def build_database_from_zip(zip_folder):
    db_path = "data/hawaii.db"
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS parcels")
    c.execute("""
        CREATE TABLE parcels (
            certificate_id TEXT,
            parcel_id TEXT,
            latitude REAL,
            longitude REAL,
            grantee TEXT,
            grantor TEXT,
            amount TEXT,
            registry_key TEXT,
            escrow_id TEXT,
            transfer_bank TEXT,
            country TEXT,
            status TEXT
        )
    """)

    total = 0
    for root, dirs, files in os.walk(zip_folder):
        for file in files:
            if file.endswith(".yaml"):
                path = os.path.join(root, file)
                txns = parse_transaction_file(path)
                for txn in txns:
                    columns = list(txn.keys())
                    values = [txn[col] for col in columns]
                    placeholders = ", ".join("?" for _ in columns)
                    c.execute(f"""
                        INSERT INTO parcels ({', '.join(columns)})
                        VALUES ({placeholders})
                    """, values)
                total += len(txns)

    conn.commit()
    conn.close()
    return total, db_path
