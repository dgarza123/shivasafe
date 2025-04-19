import sqlite3
import zipfile
import os

def build_database_from_zip(zip_path: str, out_db: str):
    """
    Unzip all your YAML/CSV files from zip_path,
    parse them, and write into a fresh SQLite at out_db.
    """
    # ensure parent folder exists
    os.makedirs(os.path.dirname(out_db), exist_ok=True)

    # for example:
    with sqlite3.connect(out_db) as conn:
        cur = conn.cursor()
        # (re)create tables…
        cur.execute("DROP TABLE IF EXISTS parcels;")
        cur.execute("""
            CREATE TABLE parcels (
                parcel_id TEXT PRIMARY KEY,
                latitude REAL,
                longitude REAL
            )
        """)
        # now unzip & load…
        with zipfile.ZipFile(zip_path) as z:
            for fname in z.namelist():
                if fname.endswith(".csv"):
                    with z.open(fname) as f:
                        # naive CSV load
                        import pandas as pd
                        df = pd.read_csv(f)
                        df.to_sql("parcels", conn, if_exists="append", index=False)
