import os
import yaml
import sqlite3
import json
import pandas as pd

DB_PATH       = "data/hawaii.db"
SOURCE_FOLDER = "evidence"
TABLE_NAME    = "parcels"

MASTER_CSV_PATHS = [
    "data/Hawaii_tmk_master.csv",
    "data/Hawaii.csv"
]

def load_master_coords():
    for path in MASTER_CSV_PATHS:
        if os.path.exists(path):
            df = pd.read_csv(path, dtype=str)
            df.columns = [c.strip().lower() for c in df.columns]
            if {"parcel_id","latitude","longitude"}.issubset(df.columns):
                coords = {
                    row["parcel_id"].strip(): (
                        float(row["latitude"]), float(row["longitude"])
                    )
                    for _, row in df.iterrows()
                    if str(row["parcel_id"]).strip()
                }
                print(f"ℹ️ Loaded {len(coords)} coords from {path}")
                return coords
    print("⚠️ No master coords CSV found; only inline GPS will be used.")
    return {}

def create_table(conn):
    conn.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
    conn.execute(f"""
    CREATE TABLE {TABLE_NAME} (
        certificate_id    TEXT,
        sha256            TEXT,
        document          TEXT,
        grantor           TEXT,
        grantee           TEXT,
        amount            TEXT,
        parcel_id         TEXT,
        parcel_valid      BOOLEAN,
        latitude          REAL,
        longitude         REAL,
        registry_key      TEXT,
        escrow_id         TEXT,
        transfer_bank     TEXT,
        country           TEXT,
        routing_code      TEXT,
        account_fragment  TEXT,
        link              TEXT,
        method            TEXT,
        signing_date      TEXT,
        former_grantors   TEXT,
        true_grantees     TEXT,
        intermediaries    TEXT
    )
    """)
    conn.commit()

def build_db():
    # Prepare DB
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    master_coords = load_master_coords()
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)
    inserted = 0

    # Walk evidence folder
    for root, _, files in os.walk(SOURCE_FOLDER):
        for fname in files:
            if not fname.lower().endswith((".yaml", ".yml")):
                continue
            path = os.path.join(root, fname)

            # 1) Try to parse the YAML, skip on error
            try:
                data = yaml.safe_load(open(path, "r", encoding="utf-8")) or {}
            except yaml.YAMLError as e:
                print(f"⚠️ Skipping invalid YAML `{fname}`: {e}")
                continue

            if not isinstance(data, dict):
                print(f"⚠️ Skipping non‐mapping YAML `{fname}`")
                continue

            # 2) Determine certificate ID
            cert = (
                data.get("certificate_number")
                or data.get("cert_id")
                or data.get("document")
                or fname
            )
            sha = data.get("sha256", "")
            doc = data.get("document", "")

            txs = data.get("transactions", [])
            if not isinstance(txs, list):
                print(f"⚠️ Skipping `{fname}`: transactions not a list")
                continue

            # 3) Insert each transaction
            for tx in txs:
                # GPS: inline or fallback
                lat = lon = None
                gps = tx.get("gps")
                if isinstance(gps, (list, tuple)) and len(gps) >= 2:
                    lat, lon = gps[0], gps[1]
                else:
                    pid = str(tx.get("parcel_id","")).strip()
                    if pid in master_coords:
                        lat, lon = master_coords[pid]

                # Nested entities (may be missing)
                re  = tx.get("related_entities", {}) or {}
                former = re.get("former_grantors", []) or []
                trueg  = re.get("true_grantees", [])  or []
                inter  = re.get("intermediaries", []) or []

                # Execute insert
                conn.execute(f"""
                    INSERT INTO {TABLE_NAME} (
                        certificate_id, sha256, document, grantor, grantee,
                        amount, parcel_id, parcel_valid, latitude, longitude,
                        registry_key, escrow_id, transfer_bank, country,
                        routing_code, account_fragment, link, method,
                        signing_date, former_grantors, true_grantees, intermediaries
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cert,
                    sha,
                    doc,
                    tx.get("grantor"),
                    tx.get("grantee"),
                    tx.get("amount"),
                    tx.get("parcel_id"),
                    bool(tx.get("parcel_valid")),
                    lat,
                    lon,
                    tx.get("registry_key"),
                    tx.get("escrow_id"),
                    tx.get("transfer_bank"),
                    tx.get("country"),
                    tx.get("routing_code"),
                    tx.get("account_fragment"),
                    tx.get("link"),
                    tx.get("method"),
                    tx.get("signing_date"),
                    json.dumps(former, ensure_ascii=False),
                    json.dumps(trueg,  ensure_ascii=False),
                    json.dumps(inter,  ensure_ascii=False),
                ))
                inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ Built {DB_PATH} with {inserted} transactions.")
    return inserted

if __name__ == "__main__":
    build_db()
