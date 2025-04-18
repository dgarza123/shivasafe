import os
import yaml
import csv
import pandas as pd

EVIDENCE_DIR = "evidence"
TMK_MASTER_PATH = "data/Hawaii.csv"
OUTPUT_CSV = "Hawaii_tmk_suppression_status.csv"

# Load TMK master
if not os.path.exists(TMK_MASTER_PATH):
    print(f"❌ TMK reference not found at {TMK_MASTER_PATH}")
    exit()

tmk_df = pd.read_csv(TMK_MASTER_PATH)
tmk_df.columns = [c.lower() for c in tmk_df.columns]
tmk_df = tmk_df.rename(columns={"tmk": "parcel_id"})
known_tmks = set(tmk_df["parcel_id"].astype(str).str.strip())

# Load YAMLs and extract all parcel references
suppression_rows = []

for root, _, files in os.walk(EVIDENCE_DIR):
    for file in files:
        if file.endswith(".yaml"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    yml = yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ Skipped {file}: {e}")
                continue

            doc = yml.get("document") or yml.get("certificate_number") or file
            for tx in yml.get("transactions", []):
                parcel_id = tx.get("parcel_id", "").strip()
                if not parcel_id:
                    continue

                classification = "Unknown"
                if parcel_id in known_tmks:
                    classification = "Public"
                elif len(parcel_id) >= 5:
                    classification = "Disappeared"
                elif parcel_id.lower().startswith("fake") or parcel_id == "000000":
                    classification = "Fabricated"

                match = tmk_df[tmk_df["parcel_id"] == parcel_id]
                latitude = match["latitude"].values[0] if not match.empty else None
                longitude = match["longitude"].values[0] if not match.empty else None

                suppression_rows.append({
                    "TMK": parcel_id,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "classification": classification,
                    "document": doc
                })

# Save result
if suppression_rows:
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["TMK", "Latitude", "Longitude", "classification", "document"])
        writer.writeheader()
        writer.writerows(suppression_rows)
    print(f"✅ Exported {len(suppression_rows)} records to {OUTPUT_CSV}")
else:
    print("⚠️ No parcels found to classify.")
