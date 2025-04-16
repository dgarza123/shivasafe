# app.py
import streamlit as st
import os
import zipfile
from database_builder import build_database_from_folder

st.set_page_config("Hawaii DB Uploader", layout="centered")

st.title("🧾 Upload ZIP: YAMLs + Parcel CSVs")
st.markdown("Upload a **single .zip** containing your `Hawaii*.csv` files and `.yaml` files.")

uploaded_file = st.file_uploader("Upload .zip", type="zip")

if uploaded_file:
    os.makedirs("uploads", exist_ok=True)

    zip_path = os.path.join("uploads", uploaded_file.name)
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())

    extract_path = os.path.join("uploads", "extracted")
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    st.success("✅ ZIP extracted. Building database...")

    count, db_path = build_database_from_folder(extract_path)

    st.success(f"✅ Database created at `{db_path}`")
    st.info(f"📦 {count} transactions written")

    with open(db_path, "rb") as f:
        st.download_button("⬇️ Download hawaii.db", f, file_name="hawaii.db")

