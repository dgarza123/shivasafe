# pages/admin.py

import streamlit as st
import os
import zipfile
import shutil
from rebuild_db import build_db

st.set_page_config("Admin Upload", layout="centered")
st.title("🔒 Admin Upload Panel")

st.markdown("Upload a `.zip` file containing multiple `.yaml` files.")

uploaded_zip = st.file_uploader("Upload ZIP file with YAMLs", type="zip")

if uploaded_zip:
    # Clear previous files
    extract_dir = "uploads/yamls"
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)

    # Save ZIP
    zip_path = os.path.join("uploads", "yamls.zip")
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.read())
    st.success("✅ ZIP uploaded")

    # Extract contents
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    st.info("📂 YAMLs extracted")

    # Build DB
    with st.spinner("🔨 Building database..."):
        try:
            db_path = "data/hawaii.db"
            if os.path.exists(db_path):
                os.remove(db_path)

            count = build_db(extract_dir, db_path)
            st.success(f"✅ Built database with {count} transactions")

            # Check for `status` column
            import sqlite3
            conn = sqlite3.connect(db_path)
            result = conn.execute("PRAGMA table_info(parcels)").fetchall()
            conn.close()
            columns = [row[1] for row in result]
            if "status" not in columns:
                st.error("❌ 'status' column missing from parcels table")

            # Download
            with open(db_path, "rb") as f:
                st.download_button("⬇️ Download hawaii.db", f, file_name="hawaii.db")

        except Exception as e:
            st.error(f"❌ Failed to build DB: {e}")
