# pages/database_builder.py

import os
import io
import zipfile
import yaml
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Build Database", layout="centered")
st.title("🔧 Build Hawaii Database from YAML Files")

DATA_DIR = "data"
UPLOAD_DIR = "uploads/extracted"
DB_PATH = os.path.join(DATA_DIR, "hawaii.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Upload form
with st.form("upload_zip"):
    zip_file = st.file_uploader("Upload a ZIP of YAML files", type=["zip"])
    submitted = st.form_submit_button("Build Database")

if submitted:
    if zip_file is None:
        st.error("Please upload a .zip file.")
        st.stop()

    # Clear upload dir
    for f in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, f))

    # Extract ZIP
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(UPLOAD_DIR)

    st.success(f"✅ ZIP extracted to {UPLOAD_DIR}")

    # Parse YAML files
    all_rows = []
    for fname in os.listdir(UPLOAD_DIR):
        if not fname.endswith(".yaml"):
            continue
        try:
            with open(os.path.join(UPLOAD_DIR, fname), "r", encoding="utf-8") as f:
                y = yaml.safe_load(f)

            sha256 = y.get("sha256", "")
            cert_id = y.get("document", os.path.splitext(fname)[0])

            for tx in y.get("transactions", []):
                row = {
                    "certificate_id": cert_id,
                    "sha256": sha256,
                    "parcel_id": tx.get("parcel_id"),
                    "parcel_valid": tx.get("parcel_valid", False),
                    "grantee": tx.get("grantee"),
                    "grantor": tx.get("grantor"),
                    "amount": tx.get("amount"),
                    "status": tx.get("status", "Unknown"),
                    "escrow_id": tx.get("escrow_id", ""),
                    "registry_key": tx.get("registry_key", ""),
                    "country": tx.get("country", ""),
                    "transfer_bank": tx.get("transfer_bank", ""),
                    "link": tx.get("link", ""),
                    "latitude": tx.get("latitude", None),
                    "longitude": tx.get("longitude", None),
                    "date_signed": tx.get("date_signed", "")
                }
                all_rows.append(row)

        except Exception as e:
            st.warning(f"⚠️ Failed to parse {fname}: {e}")

    if not all_rows:
        st.error("❌ No valid transactions found.")
        st.stop()

    # Build DB
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        st.info("⛔ Removed existing hawaii.db")

    df = pd.DataFrame(all_rows)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("parcels", conn, index=False)
    conn.close()

    st.success(f"✅ Done. {len(df)} transactions saved to {DB_PATH}")