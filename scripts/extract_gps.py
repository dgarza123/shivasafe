#!/usr/bin/env python3
"""
scripts/extract_gps.py

1) Pull every `gps: [lat,lon]` from your evidence/*.yaml
2) Dump data/gps_patch.csv  (all parcels with YAML‑provided coords)
3) Compare against data/Hawaii_tmk_master.csv to find which still lack coords
   → data/missing_gps.csv
"""
import glob
import yaml
import pandas as pd

def main():
    # 1) Read your master TMK list (with x/y that you reprojected to WGS84 already)
    master = pd.read_csv("data/Hawaii_tmk_master.csv", dtype={"parcel_id": str})

    # 2) Scan all YAMLs for gps fields
    records = []
    for fn in glob.glob("evidence/*.yaml"):
        doc = yaml.safe_load(open(fn, encoding="utf-8"))
        for txn in doc.get("transactions", []):
            gps = txn.get("gps")
            if gps:
                records.append({
                    "parcel_id": str(txn["parcel_id"]),
                    "latitude":  gps[0],
                    "longitude": gps[1],
                })

    patch = pd.DataFrame(records).drop_duplicates(subset=["parcel_id"])
    patch.to_csv("data/gps_patch.csv", index=False)
    print(f"Wrote {len(patch)} patched coords → data/gps_patch.csv")

    # 3) Any master parcels still missing?
    merged = master.merge(patch, on="parcel_id", how="left")
    missing = merged[merged["latitude"].isna()][["parcel_id"]]
    missing.to_csv("data/missing_gps.csv", index=False)
    print(f"Wrote {len(missing)} missing coords → data/missing_gps.csv")

if __name__ == "__main__":
    main()
