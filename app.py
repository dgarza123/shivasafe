import streamlit as st
import os
import hashlib
import datetime
import yaml

# Load password from config.yaml
CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
ADMIN_PASSWORD = config.get("admin_password")
if not ADMIN_PASSWORD:
    st.error("Admin password missing in config.yaml")
    st.stop()

st.set_page_config(page_title="ShivaSafe Upload", layout="wide")
st.title("ShivaSafe | Upload Evidence")

TMP_DIR = "tmp"

# Authentication
if "auth" not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    with st.container():
        st.markdown("#### 🔒 Admin Login")
        password = st.text_input("Enter admin password:", type="password")
        if password == ADMIN_PASSWORD:
            st.session_state.auth = True
            if not st.session_state.get("rerun_done"):
                st.session_state.rerun_done = True
                st.experimental_rerun()
        else:
            st.stop()

# Upload form
with st.expander("📤 Upload New Evidence", expanded=True):
    with st.form("upload_form", clear_on_submit=True):
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
        yaml_file = st.file_uploader("Upload YAML", type=["yaml", "yml"])
        submitted = st.form_submit_button("Submit")

        if submitted and pdf_file and yaml_file:
            try:
                pdf_bytes = pdf_file.read()
                hash_id = hashlib.sha256(pdf_bytes).hexdigest()[:12]
                date_stamp = datetime.datetime.now().strftime("%Y-%m-%d")
                base = f"{date_stamp}_{hash_id}"

                os.makedirs(TMP_DIR, exist_ok=True)
                with open(os.path.join(TMP_DIR, base + ".pdf"), "wb") as f:
                    f.write(pdf_bytes)
                with open(os.path.join(TMP_DIR, base + "_entities.yaml"), "wb") as f:
                    f.write(yaml_file.read())

                st.success(f"Uploaded as `{base}`")
                if not st.session_state.get("rerun_done"):
                    st.session_state.rerun_done = True
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Upload failed: {e}")
