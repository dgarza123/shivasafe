#!/usr/bin/env python3
import os
import pandas as pd
from pyproj import Transformer

def main():
    # 1) Prompt for input CSV path
    default_in = "data/Hawaii_tmk_master.csv"
    in_path = input(f"Enter path to projected CSV [{default_in}]: ").strip() or default_in
    if not os.path.exists(in_path):
        print(f"❌ File not found: {in_path}")
        return

    # 2) Prompt for output CSV path
    default_out = "data/Hawaii_tmk_master_wgs84.csv"
    out_path = input(f"Enter output path for WGS84 CSV [{default_out}]: ").strip() or default_out

    # 3) Load DataFrame
    df = pd.read_csv(in_path, dtype=str)
    required = {"parcel_id", "latitude", "longitude"}
    if not required.issubset(df.columns):
        print(f"❌ CSV must contain columns {required}; found {list(df.columns)}")
        return

    # Convert latitude/longitude to floats
    df["latitude"]  = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)

    # 4) Prompt for source EPSG (default 3564)
    epsg_default = "3564"
    epsg_in = input(f"Enter EPSG code of input projection [{epsg_default}]: ").strip() or epsg_default
    src_crs = f"EPSG:{epsg_in}"
    dst_crs = "EPSG:4326"

    # 5) Build transformer and reproject
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    lons, lats = transformer.transform(
        df["longitude"].tolist(),
        df["latitude"].tolist()
    )
    df["longitude"], df["latitude"] = lons, lats

    # 6) Save the new WGS84 CSV
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"✅ Reprojected {len(df)} rows → {out_path}")

if __name__ == "__main__":
    main()
