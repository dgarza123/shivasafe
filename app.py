import streamlit as st
import os
import zipfile
import tempfile
from rebuild_db import build_db

st.set_page_config("Upload & Build Hawaii DB", layout="centered")
st.title("📦 Upload YAML ZIP for Parcel DB")
st.markdown("Upload a `.zip` file containing `.yaml` transaction files only.")

uploaded_file = st.file_uploader("Upload a .zip of YAMLs", type="zip")

if uploaded_file:
    db_path = "data/hawaii.db"

    if os.path.exists(db_path):
        os.remove(db_path)
        st.warning("⛔ Removed existing hawaii.db")

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "upload.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmpdir)

        # Debug: List extracted YAML files
        extracted_files = [f for f in os.listdir(tmpdir) if f.endswith(".yaml")]
        if not extracted_files:
            st.error("❌ No YAML files found after extraction. Check your ZIP file.")
        else:
            st.info(f"ℹ️ YAML files found: {len(extracted_files)}")

        try:
            count = build_db(tmpdir, output_path=db_path)
            st.success(f"✅ Done. {count} transactions saved to {db_path}")
        except Exception as e:
            st.error(f"❌ Failed to build database: {e}")
