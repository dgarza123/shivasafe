# app.py

import streamlit as st
import os
import zipfile
from rebuild_db import build_db

st.set_page_config("Upload & Build Hawaii DB", layout="centered")
st.title("📦 Upload Parcel + YAML ZIP")

st.markdown("Upload a `.zip` file containing only `.yaml` transaction files.")

uploaded_file = st.file_uploader("Upload a ZIP file", type="zip")

if uploaded_file:
    db_path = "data/hawaii.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        st.warning("⛔ Removed existing hawaii.db")

    # Save zip
    os.makedirs("uploads", exist_ok=True)
    zip_path = os.path.join("uploads", uploaded_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ ZIP uploaded")

    # Extract
    extract_path = os.path.join("uploads", "yamls")
    os.makedirs(extract_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    st.info("📂 Extracted YAMLs to /uploads/yamls")

    # Build DB
    with st.spinner("🔧 Building database from YAMLs..."):
        try:
            count = build_db(extract_path)
            st.success(f"✅ Done. {count} transactions saved to {db_path}")

            # Allow download
            with open(db_path, "rb") as f:
                st.download_button("⬇️ Download hawaii.db", f, file_name="hawaii.db")
        except Exception as e:
            st.error(f"❌ Failed to build database: {e}")
