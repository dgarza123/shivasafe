# File: pages/generate_suppression_csv.py

import streamlit as st
import os
import yaml
import pandas as pd
import csv

st.set_page_config(page_title="Generate Suppression CSV", layout="wide")
st.title("📄 Generate TMK Suppression CSV")

EVIDENCE_DIR       = "evidence"
OUTPUT_CSV         = "Hawaii_tmk_suppression_status.csv"
# Try these locations for your master TMK→GPS file:
MASTER_CANDIDATES = [
    "data/Hawaii_tmk_master.csv",
    "data/Hawaii.csv",
    "/mnt/data/Hawaii_tmk_master.csv",
    "/mnt/data/Hawaii.csv",
]

# ———————————————————————————————
# 1) Locate the TMK master file
# ———————————————————————————————
master_path = None
for p in MASTER_CANDIDATES:
    if os.path.exists(p):
        master_path = p
        break

if master_path:
    st.info(f"📄 Using TMK master file: `{master_path}`")
    try:
        master_df = pd.read_csv(master_path, dtype=str)
    except Exception as e:
        st.error(f"❌ Failed to read `{master_path}`: {e}")
        st.stop()
else:
    st.error("❌ TMK master CSV not found. Checked:\n" + "\n".join(f"- {p}" for p in MASTER_CANDIDATES))
    st.info("Place your `Hawaii.csv` (with columns `parcel_id,latitude,longitude`) in `data/` or upload below.")
    uploaded = st.file_uploader("Or upload TMK master CSV now", type="csv")
    if uploaded:
        try:
            master_df = pd.read_csv(uploaded, dtype=str)
            st.success("✅ Uploaded TMK master file")
        except Exception as e:
            st.error(f"❌ Failed to parse uploaded CSV: {e}")
            st.stop()
    else:
        st.stop()

# Normalize master DataFrame
master_df.columns = [c.strip() for c in master_df.columns]
rename_map = {}
for c in master_df.columns:
    if c.lower() in ("tmk","parcel_id"):
        rename_map[c] = "parcel_id"
    if c.lower() == "latitude":
        rename_map[c] = "latitude"
    if c.lower() == "longitude":
        rename_map[c] = "longitude"
if rename_map:
    master_df = master_df.rename(columns=rename_map)
if not {"parcel_id","latitude","longitude"}.issubset(master_df.columns):
    st.error("❌ TMK master CSV must contain columns: parcel_id, latitude, longitude")
    st.stop()

master_df["parcel_id"] = master_df["parcel_id"].astype(str).str.strip()
known_tmks = set(master_df["parcel_id"])

# ———————————————————————————————
# 2) Gather YAML files
# ———————————————————————————————
yaml_paths = []
for root, _, files in os.walk(EVIDENCE_DIR):
    for fname in files:
        if fname.lower().endswith((".yaml", ".yml")):
            yaml_paths.append(os.path.join(root, fname))

if not yaml_paths:
    st.error(f"❌ No YAML files found in `{EVIDENCE_DIR}`")
    st.stop()

st.info(f"✅ Found {len(yaml_paths)} YAML file(s) in `{EVIDENCE_DIR}`")

# ———————————————————————————————
# 3) Generate suppression rows
# ———————————————————————————————
if st.button("🚀 Generate & Download Suppression CSV"):
    rows = []
    total_txs = 0

    for path in yaml_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            st.warning(f"⚠️ Skipping `{path}`: {e}")
            continue

        doc = data.get("document") or data.get("certificate_number") or os.path.basename(path)
        txs = data.get("transactions", [])
        if not isinstance(txs, list):
            continue

        for tx in txs:
            total_txs += 1
            pid = str(tx.get("parcel_id","")).strip()
            if not pid:
                continue

            # Classification logic
            if pid in known_tmks:
                status = "Public"
                lat = master_df.loc[master_df["parcel_id"] == pid, "latitude"].iloc[0]
                lon = master_df.loc[master_df["parcel_id"] == pid, "longitude"].iloc[0]
            else:
                # Well-formed TMK but missing = Disappeared
                status = "Disappeared" if len(pid) >= 5 else "Fabricated"
                lat = lon = None

            rows.append({
                "TMK": pid,
                "Latitude": lat,
                "Longitude": lon,
                "classification": status,
                "document": doc
            })

    if not rows:
        st.warning("⚠️ No transactions found to classify.")
        st.stop()

    # Save to CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["TMK","Latitude","Longitude","classification","document"])
        writer.writeheader()
        writer.writerows(rows)

    st.success(f"✅ Generated {OUTPUT_CSV} with {len(rows)} records (scanned {total_txs} transactions).")
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        st.download_button("⬇️ Download Suppression CSV", f.read(), file_name=OUTPUT_CSV, mime="text/csv")
