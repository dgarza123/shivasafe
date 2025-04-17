# pages/admin.py

import streamlit as st
import os
import shutil
import zipfile
from database_builder import build_database_from_zip

st.set_page_config(page_title="Admin Upload", layout="centered")
st.title("🔐 Admin: Upload ZIP and Build Database")

st.markdown("Upload a `.zip` containing:")
st.markdown("- A folder of `.yaml` transaction files")
st.markdown("- Optionally, CSVs like `Hawaii2020.csv`, etc.")
st.markdown("The ZIP will be extracted, and `hawaii.db` will be rebuilt.")

uploaded = st.file_uploader("Upload zip", type="zip")

if uploaded:
    st.info("Uploading ZIP...")
    os.makedirs("uploads", exist_ok=True)
    zip_path = os.path.join("uploads", uploaded.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded.read())
    st.success("✅ ZIP uploaded")

    # Extract ZIP
    extract_path = os.path.join("uploads", "extracted")
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)
    os.makedirs(extract_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    st.info("📂 ZIP extracted to /uploads/extracted")

    # Build DB
    with st.spinner("🔧 Building database..."):
        try:
            count, db_path = build_database_from_zip(extract_path)
            st.success(f"✅ Done. {count} transactions saved to {db_path}")
        except Exception as e:
            st.error(f"❌ Failed to build database: {e}")
