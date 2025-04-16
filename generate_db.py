import os
import sqlite3
import yaml

DB_PATH = "data/hawaii.db"
YAML_DIR = "evidence/"

# Ensure output folder exists
os.makedirs("data", exist_ok=True)

# Define database schema
def create_schema(conn):
    conn.execute("DROP TABLE IF EXISTS parcels")
    conn.execute("""
        CREATE TABLE parcels (
            certificate_id TEXT,
            parcel_id TEXT,
            sha256 TEXT,
            grantee TEXT,
            amount TEXT,
            date_signed TEXT,
            present_2018 INTEGER,
            present_2022 INTEGER,
            present_2025 INTEGER,
            status TEXT,
            latitude REAL,
            longitude REAL
        )
    """)
    conn.commit()

# Normalize parcel fields and insert
def load_yaml_to_db(conn):
    inserted = 0
    for fname in os.listdir(YAML_DIR):
        if not fname.endswith(".yaml"):
            continue
        path = os.path.join(YAML_DIR, fname)
        with open(path, "r") as f:
            try:
                ydata = yaml.safe_load(f)
                cert_id = ydata.get("certificate_id") or ydata.get("document", "") or fname
                sha = ydata.get("sha256", "")
                for tx in ydata.get("transactions", []):
                    parcel_id = tx.get("parcel_id", "")
                    if not parcel_id or parcel_id.lower().startswith("unknown"):
                        continue
                    row = (
                        cert_id,
                        parcel_id,
                        sha,
                        tx.get("grantee", ""),
                        tx.get("amount", ""),
                        tx.get("date_signed", ""),
                        int(tx.get("present_2018", False)),
                        int(tx.get("present_2022", False)),
                        int(tx.get("present_2025", False)),
                        tx.get("status", ""),
                        tx.get("latitude", None),
                        tx.get("longitude", None),
                    )
                    conn.execute("""
                        INSERT INTO parcels (
                            certificate_id, parcel_id, sha256, grantee, amount, date_signed,
                            present_2018, present_2022, present_2025, status, latitude, longitude
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, row)
                    inserted += 1
            except Exception as e:
                print(f"[!] Failed to process {fname}: {e}")
    conn.commit()
    print(f"[✓] Inserted {inserted} transaction(s) into hawaii.db")

# Main
if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    load_yaml_to_db(conn)
    conn.close()
    print(f"[✓] Database ready at {DB_PATH}")
