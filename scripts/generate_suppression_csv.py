#!/usr/bin/env python3
"""
scripts/generate_suppression_csv.py

Compare your year‑by‑year raw CSV dumps and the DB of ingested YAML parcels
to produce data/Hawaii_tmk_suppression_status.csv, with a `classification` for each TMK.
"""
import os
import glob
import sqlite3
import argparse
import pandas as pd

def load_year_sets(raw_dir):
    """Read every data/HawaiiYYYY.csv and return {year: set(TMK)}."""
    pattern = os.path.join(raw_dir, "Hawaii[0-9][0-9][0-9][0-9].csv")
    year_sets = {}
    for path in glob.glob(pattern):
        year = os.path.basename(path)[len("Hawaii"):len("Hawaii")+4]
        df = pd.read_csv(path, dtype=str, usecols=["TMK"])
        df["TMK"] = df["TMK"].str.strip()
        year_sets[year] = set(df["TMK"])
    return year_sets

def classify_tmk(tmk, years):
    """
    Simple rule:
      – Appeared in first year but missing in last → Suppressed After Use
      – Missing in first year but appears in last → Fabricated / Never Listed
      – Appears in both first & last → Still Public
      – Missing in both → Vanished After Use
    """
    yrs = sorted(years.keys())
    first, last = yrs[0], yrs[-1]
    in_first, in_last = tmk in years[first], tmk in years[last]
    if in_first and not in_last:
        return "Suppressed After Use"
    elif not in_first and in_last:
        return "Fabricated / Never Listed"
    elif in_first and in_last:
        return "Still Public"
    else:
        return "Vanished After Use"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db",      default="data/hawaii.db",
                   help="SQLite DB of your ingested YAML parcels")
    p.add_argument("--raw-dir", default="data",
                   help="Folder containing HawaiiYYYY.csv raw dumps")
    p.add_argument("--out",     default="data/Hawaii_tmk_suppression_status.csv",
                   help="Where to write the suppression‑status CSV")
    args = p.parse_args()

    # 1) load all TMKs in your YAML‑DB
    conn = sqlite3.connect(args.db)
    df = pd.read_sql("SELECT DISTINCT parcel_id AS TMK FROM parcels", conn)
    conn.close()

    # 2) load each year's public set
    year_sets = load_year_sets(args.raw_dir)
    if not year_sets:
        raise RuntimeError(f"No HawaiiYYYY.csv files found in {args.raw_dir}")

    # 3) classify each TMK
    rows = []
    for tmk in df["TMK"].astype(str):
        cls = classify_tmk(tmk, year_sets)
        rows.append({"TMK": tmk, "classification": cls})

    # 4) write out
    out_df = pd.DataFrame(rows)
    out_df.to_csv(args.out, index=False)
    print(f"Wrote suppression statuses → {args.out}")

if __name__ == "__main__":
    main()
