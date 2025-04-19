# database_builder.py
import os
import zipfile
import sqlite3
import yaml
import pandas as pd

def build_database_from_zip(zip_path: str, out_db: str):
    """
    Unzip a bundle of yamls + csvs, ingest into a fresh SQLite DB at out_db.
    Expects:
      - zip contains a folder "yamls/" with your *_entities.yaml files
      - zip contains a folder "csvs/" with CSVs that have parcel_id, latitude, longitude
    """

    # ensure output directory exists
    os.makedirs(os.path.dirname(out_db), exist_ok=True)

    # prepare a temp extraction folder
    tmpdir = os.path.join(os.path.dirname(out_db), "tmp_extract")
    if os.path.exists(tmpdir):
        for f in os.listdir(tmpdir):
            os.remove(os.path.join(tmpdir, f))
    else:
        os.makedirs(tmpdir)

    # extract zip
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(tmpdir)

    # open SQLite
    conn = sqlite3.connect(out_db)
    cur = conn.cursor()

    # create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parcels (
      parcel_id TEXT PRIMARY KEY,
      latitude REAL,
      longitude REAL,
      status TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
      certificate_number TEXT,
      grantor TEXT,
      grantee TEXT,
      parcel_id TEXT,
      signing_date TEXT,
      FOREIGN KEY(parcel_id) REFERENCES parcels(parcel_id)
    );
    """)

    # ingest YAMLs
    yaml_dir = os.path.join(tmpdir, "yamls")
    if os.path.isdir(yaml_dir):
        for fname in os.listdir(yaml_dir):
            if fname.lower().endswith((".yaml", ".yml")):
                path = os.path.join(yaml_dir, fname)
                with open(path, "r") as f:
                    doc = yaml.safe_load(f)
                cert = doc.get("certificate_number")
                for tx in doc.get("transactions", []):
                    cur.execute(
                        "INSERT OR IGNORE INTO transactions VALUES (?,?,?,?,?);",
                        (
                            cert,
                            tx.get("grantor"),
                            tx.get("grantee"),
                            tx.get("parcel_id"),
                            tx.get("signing_date"),
                        )
                    )

    # ingest CSVs
    csv_dir = os.path.join(tmpdir, "csvs")
    if os.path.isdir(csv_dir):
        for fname in os.listdir(csv_dir):
            if fname.lower().endswith(".csv"):
                df = pd.read_csv(os.path.join(csv_dir, fname), dtype=str)
                if {"parcel_id", "latitude", "longitude"}.issubset(df.columns):
                    for _, r in df.iterrows():
                        cur.execute(
                            "INSERT OR REPLACE INTO parcels VALUES (?,?,?,NULL);",
                            (
                                r["parcel_id"],
                                float(r["latitude"]),
                                float(r["longitude"]),
                            )
                        )

    # commit & close
    conn.commit()
    conn.close()
