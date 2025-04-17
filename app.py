# app.py

import streamlit as st
import os
import zipfile
import shutil
from rebuild_db_script import build_db  # match the filename of your script

st.set_page_config("Upload YAML DB", layout="centered")
st.title("📦 Upload YAML ZIP to Build hawaii.db")

uploaded_file = st.file_uploader("Upload a .zip containing only .yaml files", type="zip")

if uploaded_file:
    # Cleanup old db
    db_path = "data/hawaii.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        st.warning("⛔ Removed old hawaii.db")

    # Save zip
    os.makedirs("uploads", exist_ok=True)
    zip_path = os.path.join("uploads", uploaded_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ ZIP uploaded")

    # Extract ZIP
    extract_dir = os.path.join("uploads", "yamls")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
    st.info(f"📂 Extracted to {extract_dir}")

    # Rebuild database
    with st.spinner("🔧 Rebuilding hawaii.db..."):
        try:
            count = build_db(extract_dir, db_path)
            st.success(f"✅ Done. {count} transactions written to {db_path}")

            with open(db_path, "rb") as f:
                st.download_button("⬇️ Download hawaii.db", f, file_name="hawaii.db")
        except Exception as e:
            st.error(f"❌ Failed to build database: {e}")
