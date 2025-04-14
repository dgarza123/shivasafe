import streamlit as st
import os
import yaml

st.set_page_config(page_title="Upload to Root", layout="wide")
st.title("Admin: Upload File to Root Directory")

# Load admin password from config.yaml
CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
ADMIN_PASSWORD = config.get("admin_password")

# Secure access
if "auth_root" not in st.session_state:
    st.session_state.auth_root = False

if not st.session_state.auth_root:
    pw = st.text_input("Enter admin password:", type="password")
    if pw == ADMIN_PASSWORD:
        st.session_state.auth_root = True
        st.rerun()
    else:
        st.stop()

# Upload form
with st.form("upload_root_form"):
    uploaded = st.file_uploader("Select a file to upload to the app root", type=None)
    submit = st.form_submit_button("Upload")

    if submit and uploaded:
        try:
            save_path = os.path.join(".", uploaded.name)
            with open(save_path, "wb") as f:
                f.write(uploaded.read())
            st.success(f"Uploaded to root: {uploaded.name}")
        except Exception as e:
            st.error(f"Upload failed: {e}")
