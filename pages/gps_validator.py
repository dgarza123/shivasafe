import streamlit as st
import os
import yaml
import csv

EVIDENCE_FOLDER = "evidence"
OUTPUT_CSV = "missing_gps.csv"

st.set_page_config(page_title="GPS Validator", layout="wide")
st.title("📍 GPS Validator & Export")

# Step 1: Gather YAML files
yaml_files = []
for root, _, files in os.walk(EVIDENCE_FOLDER):
    for file in files:
        if file.endswith(".yaml"):
            yaml_files.append(os.path.join(root, file))

if not yaml_files:
    st.error("❌ No YAML files found in /evidence.")
    st.stop()

st.success(f"✅ Found {len(yaml_files)} YAML file(s) in /evidence.")

# Step 2: Run validator
if st.button("🚀 Run Validation + Export missing_gps.csv"):
    total_transactions = 0
    valid_gps = 0
    missing_gps_rows = []

    for path in yaml_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            st.warning(f"⚠️ Failed to read {path}: {e}")
            continue

        cert = data.get("certificate_number") or data.get("document") or os.path.basename(path)
        txs = data.get("transactions", [])
        if not isinstance(txs, list):
            continue

        for tx in txs:
            total_transactions += 1
            gps = tx.get("gps")
            parcel_id = tx.get("parcel_id", "UNKNOWN")

            if isinstance(gps, list) and len(gps) == 2 and all(isinstance(c, (float, int)) for c in gps):
                valid_gps += 1
            else:
                missing_gps_rows.append({
                    "certificate_id": cert,
                    "parcel_id": parcel_id,
                    "filename": os.path.basename(path)
                })

    # Step 3: Show results
    st.subheader("📊 Validation Results")
    st.markdown(f"- Total transactions: **{total_transactions}**")
    st.markdown(f"- With valid GPS: **{valid_gps}**")
    st.markdown(f"- Missing or invalid GPS: **{len(missing_gps_rows)}**")
    st.markdown(f"🗺️ You should see approximately **{valid_gps}** dots on the map.")

    if missing_gps_rows:
        df_export = missing_gps_rows
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["certificate_id", "parcel_id", "filename"])
            writer.writeheader()
            writer.writerows(df_export)

        with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
            st.download_button("⬇️ Download missing_gps.csv", f.read(), file_name=OUTPUT_CSV, mime="text/csv")

        st.info(f"📄 Exported {len(missing_gps_rows)} rows to {OUTPUT_CSV}")
    else:
        st.success("✅ No missing GPS data found!")
