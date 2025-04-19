# database_builder.py

import os
import glob
import sqlite3
import pandas as pd
import yaml

# —— CONFIGURE THESE —————————————————————————————————————————————————————————————
DATA_DIR       = "data"            # where your CSVs live
EVIDENCE_DIR   = "evidence"        # where your YAMLs live
OUT_DB         = os.path.join(DATA_DIR, "hawaii.db")
CSV_PATTERNS   = ["Hawaii_tmk_master.csv",
                  "Hawaii2020.csv","Hawaii2021.csv",
                  "Hawaii2023.csv","Hawaii2024.csv"]
# ————————————————————————————————————————————————————————————————————————————————

def make_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parcels (
      parcel_id TEXT PRIMARY KEY,
      county    TEXT,
      division  TEXT,
      island    TEXT,
      zone      TEXT,
      section   TEXT,
      plat      TEXT,
      plat1     TEXT,
      parcel    TEXT,
      parcel1   TEXT,
      GISAcres  REAL,
      qpub_link TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
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
      signing_date     TEXT,
      FOREIGN KEY(parcel_id) REFERENCES parcels(parcel_id)
    );
    """)
    # …and any other tables you need…

def load_csvs(cur):
    for pattern in CSV_PATTERNS:
        path = os.path.join(DATA_DIR, pattern)
        print(f" → Loading {pattern}…")
        df = pd.read_csv(path, dtype=str)

        # drop exact duplicate parcel_ids in this file
        df = df.drop_duplicates(subset=["parcel_id"])

        # Insert (or replace) every row
        for _, row in df.iterrows():
            cur.execute("""
            INSERT OR REPLACE INTO parcels
              (parcel_id, county, division, island, zone,
               section, plat, plat1, parcel, parcel1,
               GISAcres, qpub_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["parcel_id"],
                row.get("county",""),
                row.get("division",""),
                row.get("island",""),
                row.get("zone",""),
                row.get("section",""),
                row.get("plat",""),
                row.get("plat1",""),
                row.get("parcel",""),
                row.get("parcel1",""),
                float(row.get("GISAcres") or 0),
                row.get("qpub_link",""),
            ))
    print(" ✔ CSVs loaded.")

def load_yaml_evidence(cur):
    for fn in glob.glob(os.path.join(EVIDENCE_DIR,"*_entities.yaml")):
        print(f" → Parsing {os.path.basename(fn)}…")
        with open(fn) as f:
            doc = yaml.safe_load(f)
        cert = doc.get("certificate_number")
        for tx in doc.get("transactions", []):
            pid = tx.get("parcel_id")
            if not pid:
                continue
            # optional: enforce that YAML parcel_ids are strings
            pid = str(pid)
            cur.execute("""
            INSERT OR REPLACE INTO transactions
              (parcel_id, grantor, grantee, amount,
               registry_key, escrow_id, transfer_bank,
               country, routing_code, account_fragment,
               link, signing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid,
                tx.get("grantor",""),
                tx.get("grantee",""),
                tx.get("amount",""),
                tx.get("registry_key",""),
                tx.get("escrow_id",""),
                tx.get("transfer_bank",""),
                tx.get("country",""),
                tx.get("routing_code",""),
                tx.get("account_fragment",""),
                tx.get("link",""),
                tx.get("signing_date",""),
            ))
    print(" ✔ YAML evidence loaded.")

def build_database():
    # delete old DB so we start clean
    if os.path.exists(OUT_DB):
        os.remove(OUT_DB)

    conn = sqlite3.connect(OUT_DB)
    cur  = conn.cursor()

    make_tables(cur)
    load_csvs(cur)
    load_yaml_evidence(cur)

    conn.commit()
    conn.close()
    print(f"🏁 Database built at {OUT_DB}")

if __name__ == "__main__":
    build_database()
