import streamlit as st
import os
from login_manager import require_editor
from google_drive_manager import upload_to_drive

st.set_page_config(page_title="Upload to Drive", layout="centered")
require_editor()

st.title("📤 Upload Evidence to Google Drive")

with st.form("upload_form"):
    uploaded_file = st.file_uploader("Choose a YAML or PDF file", type=["yaml", "pdf"])
    submit = st.form_submit_button("Upload")

    if submit:
        if uploaded_file is None:
            st.error("No file selected.")
        else:
            temp_path = os.path.join("temp", uploaded_file.name)
            os.makedirs("temp", exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            try:
                file_id = upload_to_drive(temp_path)
                st.success(f"Uploaded to Drive (ID: {file_id})")
            except Exception as e:
                st.error(f"Upload failed: {e}")

            os.remove(temp_path)
