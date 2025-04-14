import streamlit as st
import os
import yaml

st.set_page_config(page_title="Root File Upload", layout="wide")
st.title("Admin: Upload File to Root Directory")

# Load admin password
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
ADMIN_PASSWORD = config.get("admin_password")

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
    uploaded = st.file_uploader("Choose a file to upload to the root directory", type=None)
    submit = st.form_submit_button("Upload")

    if submit and uploaded:
        try:
            bytes_data = uploaded.read()
            if len(bytes_data) == 0:
                st.error("Upload failed: File is empty.")
            else:
                out_path = os.path.join(".", uploaded.name)
                with open(out_path, "wb") as f:
                    f.write(bytes_data)
                st.success(f"✅ Uploaded to: {uploaded.name} ({len(bytes_data)} bytes)")
                st.markdown("**Preview of content:**")
                preview = bytes_data[:500].decode("utf-8", errors="ignore")
                st.code(preview)
        except Exception as e:
            st.error(f"Upload failed: {e}")
