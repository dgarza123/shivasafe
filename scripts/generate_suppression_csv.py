# scripts/generate_suppression_csv.py
import sqlite3
import pandas as pd
import argparse

def main(db_path, out_csv):
    conn = sqlite3.connect(db_path)
    # This query assumes your parcels table has a 'suppressed' boolean column
    df = pd.read_sql_query(
        "SELECT parcel_id, suppressed FROM parcels ORDER BY parcel_id", 
        conn,
        dtype=str
    )
    # rename to match the app’s expectation
    df.columns = ["parcel_id", "suppression_status"]
    df.to_csv(out_csv, index=False)
    print(f"Wrote suppression CSV → {out_csv}")

if __name__=="__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--db",  help="path to data/hawaii.db", required=True)
    p.add_argument("--out", help="where to write Hawaii_tmk_suppression_status.csv", required=True)
    args = p.parse_args()
    main(args.db, args.out)