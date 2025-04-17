# -------------------------- app.py --------------------------
import streamlit as st
import os
import zipfile
from database_builder import build_database_from_zip

st.set_page_config("Upload & Build Hawaii DB", layout="centered")
st.title("📦 Upload Parcel + YAML ZIP")

uploaded_file = st.file_uploader("Upload a .zip file with YAML files", type="zip")

if uploaded_file:
    db_path = "data/hawaii.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        st.warning("❌ Removed existing hawaii.db")

    extract_path = "uploads/extracted"
    os.makedirs(extract_path, exist_ok=True)

    zip_path = os.path.join("uploads", uploaded_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ ZIP uploaded")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    st.info("📂 ZIP extracted to uploads/extracted")

    with st.spinner("🔧 Building database..."):
        try:
            count = build_database_from_zip(extract_path, db_path)
            st.success(f"✅ Done. {count} transactions saved to {db_path}")
        except Exception as e:
            st.error(f"❌ Failed to build database: {e}")
