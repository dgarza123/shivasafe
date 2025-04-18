import os
import yaml
import sqlite3
from scripts.tmk_checker import get_parcel_status

DB_PATH = "data/hawaii.db"
TABLE_NAME = "parcels"
SOURCE_FOLDER = "evidence"

def create_table(conn):
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            certificate_id TEXT,
            sha256 TEXT,
            filename TEXT,
            parcel_id TEXT,
            latitude REAL,
            longitude REAL,
            grantor TEXT,
            grantee TEXT,
            country TEXT,
            status TEXT
        )
    """)
    conn.commit()

def parse_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_db():
    if not os.path.exists(SOURCE_FOLDER):
        raise FileNotFoundError(f"Missing folder: {SOURCE_FOLDER}")

    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    inserted = 0
    yaml_paths = [os.path.join(root, f)
                  for root, _, files in os.walk(SOURCE_FOLDER)
                  for f in files if f.lower().endswith(".yaml")]

    print(f"\n📁 Scanning {len(yaml_paths)} YAML file(s)...\n")

    for path in yaml_paths:
        try:
            data = parse_yaml(path)
            cert = data.get("certificate_number")
            sha = data.get("sha256", "")
            filename = data.get("document", "")

            txs = data.get("transactions", [])
            if not isinstance(txs, list):
                print(f"⚠️ Skipped {path}: transactions not a list")
                continue

            for i, tx in enumerate(txs):
                parcel = tx.get("parcel_id") or tx.get("parcel")
                gps = tx.get("gps", [])
                lat = gps[0] if isinstance(gps, list) and len(gps) >= 2 else None
                lon = gps[1] if isinstance(gps, list) and len(gps) >= 2 else None

                grantor = tx.get("grantor", "").strip()
                grantee = tx.get("grantee", "").strip()
                country = tx.get("country", "").strip()
                status = get_parcel_status(parcel)

                if not (cert and grantor and grantee and parcel):
                    print(f"⚠️ Skipped TX {i+1} in {path}: missing critical fields")
                    continue

                conn.execute(f"""
                    INSERT INTO {TABLE_NAME} (
                        certificate_id, sha256, filename,
                        parcel_id, latitude, longitude,
                        grantor, grantee, country, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cert, sha, filename,
                    parcel, lat, lon,
                    grantor, grantee, country, status
                ))
                inserted += 1
                print(f"✅ Inserted TX {i+1} from {path} [{status}]")

        except Exception as e:
            print(f"❌ Error in {path}: {e}")

    conn.commit()
    conn.close()
    print(f"\n✅ Done. Inserted {inserted} transaction(s).\n")
    return inserted
