# database_builder.py

import os
import pandas as pd
import yaml
import sqlite3

def build_database_from_folder(folder_path, output_db="data/hawaii.db"):
    parcel_snapshots = {}

    for year in ["2015", "2018", "2022", "2025"]:
        csv_path = os.path.join(folder_path, f"Hawaii{year}.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path, dtype=str)
            parcel_snapshots[year] = df
            print(f"[✓] Loaded {csv_path} with {len(df)} rows")
        else:
            print(f"[!] Missing: {csv_path}")

    # Load YAMLs
    yaml_files = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.endswith(".yaml"):
                yaml_files.append(os.path.join(root, f))

    yamls = []
    for path in yaml_files:
        try:
            with open(path, "r") as f:
                doc = yaml.safe_load(f)
                doc["_source_file"] = os.path.basename(path)
                yamls.append(doc)
        except Exception as e:
            print(f"[!] Error loading YAML {path}: {e}")

    print(f"[✓] Parsed {len(yamls)} YAMLs")

    os.makedirs(os.path.dirname(output_db), exist_ok=True)
    conn = sqlite3.connect(output_db)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS parcels")
    cur.execute("""
    CREATE TABLE parcels (
        certificate_id TEXT,
        parcel_id TEXT,
        sha256 TEXT,
        grantee TEXT,
        amount TEXT,
        date TEXT,
        present_2015 INTEGER,
        present_2018 INTEGER,
        present_2022 INTEGER,
        present_2025 INTEGER,
        status TEXT,
        latitude REAL,
        longitude REAL,
        source_file TEXT
    )
    """)

    def check_presence(pid, year):
        df = parcel_snapshots.get(year)
        return pid in df.values if df is not None else False

    inserted = 0
    for doc in yamls:
        try:
            sha = doc.get("sha256", "")
            cert = doc.get("certificate_id") or doc.get("cert_id") or doc.get("document") or doc.get("_source_file")

            for tx in doc.get("transactions", []):
                pid = tx.get("parcel_id", "")
                if not pid or pid.lower().startswith("unknown"):
                    continue

                p15 = check_presence(pid, "2015")
                p18 = check_presence(pid, "2018")
                p22 = check_presence(pid, "2022")
                p25 = check_presence(pid, "2025")

                if p18 and not p25:
                    status = "Disappeared"
                elif p15 and not p18:
                    status = "Erased"
                elif not any([p15, p18, p22, p25]):
                    status = "Fabricated"
                else:
                    status = "Public"

                date = tx.get("date_signed") or tx.get("date_closed")
                row = (
                    cert,
                    pid,
                    sha,
                    tx.get("grantee", ""),
                    tx.get("amount", ""),
                    date,
                    int(p15), int(p18), int(p22), int(p25),
                    status,
                    tx.get("latitude", None),
                    tx.get("longitude", None),
                    doc.get("_source_file")
                )

                if all(row[:6]):  # Check for essential fields
                    cur.execute("INSERT INTO parcels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
                    inserted += 1
                else:
                    print(f"[!] Skipped incomplete row: {row}")

        except Exception as e:
            print(f"[!] Error in document {doc.get('_source_file')}: {e}")

    conn.commit()
    conn.close()
    print(f"[✓] Wrote {inserted} valid transactions to {output_db}")
    return inserted, output_db
