import streamlit as st
import os
import hashlib
import datetime
import yaml
import glob

# Load password from config.yaml
CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
ADMIN_PASSWORD = config.get("admin_password")
if not ADMIN_PASSWORD:
    st.error("Admin password missing in config.yaml")
    st.stop()

st.set_page_config(page_title="ShivaSafe | Upload Evidence", layout="wide")
st.title("📤 ShivaSafe Evidence Uploader")

TMP_DIR = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)

# Authentication
if "auth" not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("#### 🔒 Admin Login")
    password = st.text_input("Enter admin password:", type="password")
    if password == ADMIN_PASSWORD:
        st.session_state.auth = True
        st.rerun()  # FIXED HERE
    else:
        st.stop()

# Upload form
with st.expander("📎 Upload New Evidence Pair", expanded=True):
    with st.form("upload_form", clear_on_submit=True):
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
        yaml_file = st.file_uploader("Upload YAML", type=["yaml", "yml"])
        submitted = st.form_submit_button("Submit")

        if submitted and pdf_file and yaml_file:
            try:
                pdf_bytes = pdf_file.read()
                hash_id = hashlib.sha256(pdf_bytes).hexdigest()
                short_hash = hash_id[:12]
                date_stamp = datetime.datetime.now().strftime("%Y-%m-%d")
                base = f"{date_stamp}_{short_hash}"

                pdf_path = os.path.join(TMP_DIR, base + ".pdf")
                yaml_path = os.path.join(TMP_DIR, base + "_entities.yaml")

                with open(pdf_path, "wb") as f:
                    f.write(pdf_bytes)
                with open(yaml_path, "wb") as f:
                    f.write(yaml_file.read())

                st.success(f"✅ Uploaded: `{os.path.basename(pdf_path)}` and `{os.path.basename(yaml_path)}`")
                st.code(f"SHA-256: {hash_id}", language="bash")
                st.rerun()  # FIXED HERE
            except Exception as e:
                st.error(f"Upload failed: {e}")

# Summary panel
yaml_files = glob.glob("evidence/*_entities.yaml")
st.markdown("---")
st.subheader("📂 Current Evidence")
st.write(f"Total YAML Evidence Files: **{len(yaml_files)}**")