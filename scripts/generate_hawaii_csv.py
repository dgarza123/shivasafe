import os
import sqlite3
import pandas as pd

DB_PATH = "data/hawaii.db"
OUTPUT_CSV = "Hawaii.csv"

# Step 1: Load all parcel data from hawaii.db
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT DISTINCT parcel_id, present_2015, present_2018, present_2022, present_2025 FROM parcels", conn)
conn.close()

# Step 2: Normalize TMK column
df["parcel_id"] = df["parcel_id"].astype(str).str.strip()
df.dropna(subset=["parcel_id"], inplace=True)

# Step 3: Scan all CSVs for lat/lon matches
coord_sources = []
for fname in os.listdir():
    if fname.endswith(".csv") and fname != OUTPUT_CSV:
        try:
            src = pd.read_csv(fname)
            # Rename columns to match expected
            if "TMK" in src.columns:
                src = src.rename(columns={"TMK": "parcel_id"})
            elif "tmk" in src.columns:
                src = src.rename(columns={"tmk": "parcel_id"})

            for col in ["latitude", "lat"]:
                if col in src.columns:
                    src = src.rename(columns={col: "lat"})
                    break
            for col in ["longitude", "lon"]:
                if col in src.columns:
                    src = src.rename(columns={col: "lon"})
                    break

            if "parcel_id" in src.columns and "lat" in src.columns and "lon" in src.columns:
                coord_sources.append(src[["parcel_id", "lat", "lon"]])
        except Exception as e:
            print(f"[!] Skipped {fname}: {e}")

# Step 4: Combine and deduplicate coordinate sources
if coord_sources:
    coords = pd.concat(coord_sources).drop_duplicates(subset="parcel_id")
    coords["parcel_id"] = coords["parcel_id"].astype(str).str.strip()
    print(f"[✔] Loaded coordinates from {len(coord_sources)} files")
else:
    coords = pd.DataFrame(columns=["parcel_id", "lat", "lon"])
    print("[!] No coordinate sources found. Coordinates will be blank.")

# Step 5: Merge coordinates into suppression dataset
merged = pd.merge(df, coords, on="parcel_id", how="left")

# Step 6: Add suppression status label
def classify(row):
    if row["present_2015"] and row["present_2022"] and not row["present_2025"]:
        return "Disappeared"
    elif row["present_2015"] and not row["present_2022"] and not row["present_2025"]:
        return "Erased"
    elif not row["present_2015"] and row["present_2025"]:
        return "Fabricated"
    elif all([row["present_2015"], row["present_2018"], row["present_2022"], row["present_2025"]]):
        return "Public"
    return "Other"

merged["status"] = merged.apply(classify, axis=1)

# Step 7: Save final CSV
merged.to_csv(OUTPUT_CSV, index=False)
print(f"[✔] Hawaii.csv generated with {len(merged)} parcels.")
