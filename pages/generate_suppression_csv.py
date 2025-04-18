import streamlit as st
import os
import yaml
import pandas as pd
import csv

st.set_page_config(page_title="Generate Suppression CSV", layout="wide")
st.title("📄 Generate TMK Suppression CSV")

EVIDENCE_DIR = "evidence"
TMK_MASTER_PATH = "data/Hawaii.csv"
OUTPUT_CSV = "Hawaii_tmk_suppression_status.csv"

# Load TMK master list
if not os.path.exists(TMK_MASTER_PATH):
    st.error(f"❌ Missing required file: {TMK_MASTER_PATH}")
    st.stop()

tmk_df = pd.read_csv(TMK_MASTER_PATH)
tmk_df.columns = [c.lower() for c in tmk_df.columns]
tmk_df = tmk_df.rename(columns={"tmk": "parcel_id"})
known_tmks = set(tmk_df["parcel_id"].astype(str).str.strip())

# Button to trigger generation
if st.button("🚀 Generate Hawaii_tmk_suppression_status.csv"):
    suppression_rows = []
    yaml_count = 0
    tx_count = 0

    for root, _, files in os.walk(EVIDENCE_DIR):
        for file in files:
            if file.endswith(".yaml"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        yml = yaml.safe_load(f)
                except Exception as e:
                    st.warning(f"⚠️ Skipped {file}: {e}")
                    continue

                doc = yml.get("document") or yml.get("certificate_number") or file
                yaml_count += 1
                for tx in yml.get("transactions", []):
                    tx_count += 1
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

    # Save CSV
    if suppression_rows:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["TMK", "Latitude", "Longitude", "classification", "document"])
            writer.writeheader()
            writer.writerows(suppression_rows)

        st.success(f"✅ Generated suppression CSV with {len(suppression_rows)} records from {yaml_count} files.")
        with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
            st.download_button("⬇️ Download CSV", f.read(), file_name=OUTPUT_CSV, mime="text/csv")
    else:
        st.warning("⚠️ No parcels found to classify.")
