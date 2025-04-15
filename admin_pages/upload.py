
import streamlit as st
import os
import hashlib
import datetime
import yaml

# Load config
CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
ADMIN_PASSWORD = config.get("admin_password")

st.set_page_config(page_title="Upload Evidence", layout="wide")
st.title("Upload Evidence Files")

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# Authenticate
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("Admin Login")
    password = st.text_input("Enter admin password:", type="password")
    if password == ADMIN_PASSWORD:
        st.session_state.auth = True
        st.rerun()
    else:
        st.stop()

# Upload form
with st.form("upload_form", clear_on_submit=True):
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    yaml_file = st.file_uploader("Upload YAML", type=["yaml", "yml"])
    submitted = st.form_submit_button("Submit")

    if submitted and pdf_file and yaml_file:
        try:
            pdf_bytes = pdf_file.read()
            hash_full = hashlib.sha256(pdf_bytes).hexdigest()
            hash_short = hash_full[:12]
            date_stamp = datetime.datetime.now().strftime("%Y-%m-%d")
            base = f"{date_stamp}_{hash_short}"

            pdf_path = os.path.join(EVIDENCE_DIR, base + ".pdf")
            yaml_path = os.path.join(EVIDENCE_DIR, base + "_entities.yaml")

            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            with open(yaml_path, "wb") as f:
                f.write(yaml_file.read())

            st.success(f"Uploaded successfully as {base}")
            st.code(f"SHA-256: {hash_full}", language="text")
            st.rerun()
        except Exception as e:
            st.error(f"Upload failed: {e}")
