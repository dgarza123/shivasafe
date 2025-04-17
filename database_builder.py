import os
import yaml
import sqlite3

def build_database_from_folder(folder_path):
    db_path = "data/hawaii.db"
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS parcels (
            certificate_id TEXT,
            parcel_id TEXT,
            parcel_valid BOOLEAN,
            grantor TEXT,
            grantee TEXT,
            amount TEXT,
            escrow_id TEXT,
            registry_key TEXT,
            country TEXT,
            transfer_bank TEXT,
            link TEXT,
            date_signed TEXT,
            sha256 TEXT,
            filename TEXT,
            status TEXT
        )
    """)

    conn.commit()

    count = 0

    for fname in os.listdir(folder_path):
        if not fname.endswith(".yaml"):
            continue

        full_path = os.path.join(folder_path, fname)
        with open(full_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        sha = data.get("sha256", "")
        document = data.get("document", "")
        for tx in data.get("transactions", []):
            values = (
                tx.get("cert_id", ""),
                tx.get("parcel_id", ""),
                str(tx.get("parcel_valid", True)),
                tx.get("grantor", ""),
                tx.get("grantee", ""),
                tx.get("amount", ""),
                tx.get("escrow_id", ""),
                tx.get("registry_key", ""),
                tx.get("country", ""),
                tx.get("transfer_bank", ""),
                tx.get("link", ""),
                tx.get("date_signed", ""),
                sha,
                document,
                "Disappeared" if tx.get("parcel_valid") is False else "Public"
            )
            cur.execute("INSERT INTO parcels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
            count += 1

    conn.commit()
    conn.close()
    return count, db_path
