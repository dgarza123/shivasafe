# database_builder.py

import os
import sqlite3
import pandas as pd
import yaml

DATA_DIR      = "data"
DB_PATH       = os.path.join(DATA_DIR, "hawaii.db")
YAML_DIR      = "evidence"
CSV_YEARS     = ["Hawaii2020.csv", "Hawaii2021.csv",
                 "Hawaii2023.csv", "Hawaii2024.csv"]
EXTRA_CSVS    = ["gps_patch.csv", "missing_gps.csv", "Hawaii_tmk_suppression_status.csv"]

def build_database():
    # 1) Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)

    # 2) Delete old DB if present
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    # 3) Create new SQLite connection
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # 4) Ingest year‑by‑year TMK CSVs
    for fname in CSV_YEARS:
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        df = pd.read_csv(path, dtype=str)
        df.to_sql(f"parcels_{fname.split('.')[0]}", conn, index=False)

    # 5) Ingest extra lookup CSVs
    for fname in EXTRA_CSVS:
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        df = pd.read_csv(path, dtype=str)
        tbl = os.path.splitext(fname)[0]
        df.to_sql(tbl, conn, index=False)

    # 6) Ingest all YAML evidence files
    cur.execute("""
        CREATE TABLE evidence (
            certificate_number TEXT,
            sha256             TEXT,
            document           TEXT,
            grantor            TEXT,
            grantee            TEXT,
            amount             TEXT,
            parcel_id          TEXT,
            registry_key       TEXT,
            escrow_id          TEXT,
            transfer_bank      TEXT,
            country            TEXT,
            routing_code       TEXT,
            account_fragment   TEXT,
            link               TEXT,
            method             TEXT,
            signing_date       TEXT
        )
    """)
    for fname in os.listdir(YAML_DIR):
        if not fname.lower().endswith(".yaml"):
            continue
        with open(os.path.join(YAML_DIR, fname)) as f:
            data = yaml.safe_load(f)
        cert = data.get("certificate_number")
        sha  = data.get("sha256")
        doc  = data.get("document")
        for tx in data.get("transactions", []):
            cur.execute("""
                INSERT INTO evidence (
                    certificate_number, sha256, document, grantor, grantee, amount,
                    parcel_id, registry_key, escrow_id, transfer_bank, country,
                    routing_code, account_fragment, link, method, signing_date
                ) VALUES (
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                )
            """, [
                cert, sha, doc,
                tx.get("grantor"),
                tx.get("grantee"),
                tx.get("amount"),
                tx.get("parcel_id"),
                tx.get("registry_key"),
                tx.get("escrow_id"),
                tx.get("transfer_bank"),
                tx.get("country"),
                tx.get("routing_code"),
                tx.get("account_fragment"),
                tx.get("link"),
                tx.get("method"),
                tx.get("signing_date"),
            ])

    # 7) Finalize
    conn.commit()
    conn.close()
