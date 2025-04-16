# app.py
import streamlit as st
import os
import zipfile
from database_builder import build_database_from_folder

st.set_page_config("Upload & Build Hawaii DB", layout="centered")
st.title("📦 Upload Parcel + YAML ZIP")
st.markdown("Upload a `.zip` file containing:")
st.markdown("- `Hawaii2015.csv`, `Hawaii2018.csv`, etc.")
st.markdown("- A folder of `.yaml` transaction files")

uploaded_file = st.file_uploader("Upload a single .zip file", type="zip")

if uploaded_file:
    # Clear old DB if exists
    db_path = "data/hawaii.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        st.warning("⛔ Removed existing hawaii.db")

    # Save upload
    os.makedirs("uploads", exist_ok=True)
    zip_path = os.path.join("uploads", uploaded_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ ZIP uploaded")

    # Extract to subfolder
    extract_path = os.path.join("uploads", "extracted")
    os.makedirs(extract_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    st.info("📂 ZIP extracted to /uploads/extracted")

    # Build DB
    with st.spinner("🔧 Building database..."):
        try:
            count, built_db = build_database_from_folder(extract_path)
            st.success(f"✅ Done. {count} transactions saved to {built_db}")

            # Download button
            with open(built_db, "rb") as f:
                st.download_button("⬇️ Download hawaii.db", f, file_name="hawaii.db")
        except Exception as e:
            st.error(f"❌ Failed to build database: {e}")
