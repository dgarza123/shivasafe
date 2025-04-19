# pages/data_builder.py

import streamlit as st
import sqlite3
import yaml
from pathlib import Path
import pandas as pd

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
DB_PATH      = Path("data/hawaii.db")
EVIDENCE_DIR = Path("evidence")
DATA_DIR     = Path("data")

# -----------------------------------------------------------------------------
# SCHEMA BUILDERS
# -----------------------------------------------------------------------------
def build_parcels_table(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parcels (
      parcel_id TEXT PRIMARY KEY
    )
    """)

def build_evidence_table(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
      id               INTEGER PRIMARY KEY AUTOINCREMENT,
      parcel_id        TEXT,
      grantor          TEXT,
      grantee          TEXT,
      amount           TEXT,
      registry_key     TEXT,
      escrow_id        TEXT,
      transfer_bank    TEXT,
      country          TEXT,
      routing_code     TEXT,
      account_fragment TEXT,
      link             TEXT,
      method           TEXT,
      signing_date     TEXT,
      latitude         REAL,
      longitude        REAL,
      yaml_file        TEXT,
      FOREIGN KEY(parcel_id) REFERENCES parcels(parcel_id)
    )
    """)

def build_year_status_table(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS year_status (
      parcel_id TEXT,
      year      INTEGER,
      status    TEXT,
      PRIMARY KEY(parcel_id, year),
      FOREIGN KEY(parcel_id) REFERENCES parcels(parcel_id)
    )
    """)

# -----------------------------------------------------------------------------
# DATA INGESTION
# -----------------------------------------------------------------------------
def ingest_yamls(cur):
    for path in sorted(EVIDENCE_DIR.glob("*.yaml")):
        with open(path, "r") as f:
            for doc in yaml.safe_load_all(f):
                # handle both { … transactions: […] } and bare [ … ] formats
                txs = []
                if isinstance(doc, dict):
                    txs = doc.get("transactions", [])
                elif isinstance(doc, list):
                    txs = doc

                for tx in txs:
                    pid = tx.get("parcel_id")
                    if not pid:
                        continue
                    pid = str(pid)

                    # ensure parcel exists
                    cur.execute(
                        "INSERT OR IGNORE INTO parcels(parcel_id) VALUES (?)",
                        (pid,)
                    )

                    # extract gps if present
                    lat = lon = None
                    gps = tx.get("gps")
                    if isinstance(gps, (list, tuple)) and len(gps) >= 2:
                        lat, lon = gps[0], gps[1]

                    # insert evidence (now 16 placeholders for 16 columns)
                    cur.execute("""
                        INSERT OR IGNORE INTO evidence (
                          parcel_id, grantor, grantee, amount,
                          registry_key, escrow_id, transfer_bank,
                          country, routing_code, account_fragment,
                          link, method, signing_date,
                          latitude, longitude, yaml_file
                        ) VALUES (
                          ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                        )
                    """, (
                        pid,
                        tx.get("grantor"),
                        tx.get("grantee"),
                        tx.get("amount"),
                        tx.get("registry_key"),
                        tx.get("escrow_id"),
                        tx.get("transfer_bank"),
                        tx.get("country"),
                        tx.get("routing_code"),
                        tx.get("account_fragment"),
                        tx.get("link"),
                        tx.get("method"),
                        tx.get("signing_date"),
                        lat,
                        lon,
                        path.name
                    ))

def ingest_csvs(cur):
    for path in sorted(DATA_DIR.glob("Hawaii*.csv")):
        # infer year from filename, e.g. "Hawaii2020.csv"
        try:
            year = int(path.stem.replace("Hawaii", ""))
        except ValueError:
            st.warning(f"Skipping {path.name}: can't infer year")
            continue

        df = pd.read_csv(path, dtype=str)
        if "parcel_id" not in df.columns:
            st.warning(f"Skipping {path.name}: no parcel_id column")
            continue

        for pid in df["parcel_id"].astype(str).unique():
            cur.execute(
                "INSERT OR IGNORE INTO parcels(parcel_id) VALUES (?)",
                (pid,)
            )
            cur.execute("""
                INSERT OR REPLACE INTO year_status(parcel_id, year, status)
                VALUES (?, ?, ?)
            """, (pid, year, "present"))

# -----------------------------------------------------------------------------
# STREAMLIT PAGE
# -----------------------------------------------------------------------------
def main():
    st.title("🔄 Data Builder")
    st.write("Ingest all YAML & CSV into `data/hawaii.db`.")

    if st.button("Rebuild Database"):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        build_parcels_table(cur)
        build_evidence_table(cur)
        build_year_status_table(cur)

        ingest_yamls(cur)
        ingest_csvs(cur)

        conn.commit()
        conn.close()
        st.success("✅ Database rebuilt!")

if __name__ == "__main__":
    main()
