import os
import sqlite3
import yaml

DB_PATH = "data/hawaii.db"

def build_db(yaml_folder):
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the parcels table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parcels (
        certificate_id TEXT,
        parcel_id TEXT,
        parcel_valid BOOLEAN,
        grantor TEXT,
        grantee TEXT,
        amount TEXT,
        registry_key TEXT,
        escrow_id TEXT,
        date_signed TEXT,
        transfer_bank TEXT,
        country TEXT,
        link TEXT,
        status TEXT
    )
    """)

    total = 0
    for fname in os.listdir(yaml_folder):
        if not fname.endswith(".yaml"):
            continue
        path = os.path.join(yaml_folder, fname)
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                for tx in data.get("transactions", []):
                    row = (
                        data.get("certificate_id"),
                        tx.get("parcel_id"),
                        tx.get("parcel_valid"),
                        tx.get("grantor"),
                        tx.get("grantee"),
                        tx.get("amount"),
                        tx.get("registry_key"),
                        tx.get("escrow_id"),
                        tx.get("date_signed"),
                        tx.get("transfer_bank"),
                        tx.get("country"),
                        tx.get("link"),
                        "Public" if tx.get("parcel_valid") else "Disappeared"
                    )
                    cursor.execute("INSERT INTO parcels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
                    total += 1
            except Exception as e:
                print(f"[!] Skipped {fname}: {e}")

    conn.commit()
    conn.close()
    return total
