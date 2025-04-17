import os
import shutil
import streamlit as st

st.set_page_config(page_title="Upload YAML ZIP", layout="centered")
st.title("📦 Upload ZIP to Docker Upload Folder")

SOURCE_PATH = st.text_input("Path to your yamls.zip file", value="/path/to/yamls.zip")
DEST_DIR = "upload"
DEST_PATH = os.path.join(DEST_DIR, "yamls.zip")

if st.button("Upload ZIP"):
    if not os.path.isfile(SOURCE_PATH):
        st.error(f"File not found: {SOURCE_PATH}")
    else:
        os.makedirs(DEST_DIR, exist_ok=True)
        shutil.copy(SOURCE_PATH, DEST_PATH)
        st.success(f"✅ Copied to {DEST_PATH}")
