import streamlit as st
import os
import yaml
from datetime import datetime

# ✅ Ensure imports work from root
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from login_manager import require_editor
from google_drive_manager import upload_to_drive
from drive_sync import sync_drive_to_local

# ✅ Require editor access
require_editor()

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🔐 Admin Control Panel")

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# === Evidence File Manager ===
st.subheader("🗂 Manage Uploaded Evidence")

yaml_files = sorted([f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml")])
if not yaml_files:
    st.info("No evidence YAMLs found in /evidence/")
else:
    for yaml_name in yaml_files:
        base = yaml_name.replace("_entities.yaml", "")
        yaml_path = os.path.join(EVIDENCE_DIR, yaml_name)
        pdf_path = os.path.join(EVIDENCE_DIR, base + ".pdf")

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            sha = data.get("sha256", "unknown")
            tx_count = len(data.get("transactions", []))
            mod_time = datetime.fromtimestamp(os.path.getmtime(yaml_path)).strftime('%Y-%m-%d %H:%M:%S')

            st.markdown(f"### `{base}`")
            st.caption(f"Last Modified: {mod_time}")
            st.markdown(f"- SHA256: `{sha}`")
            st.markdown(f"- Transactions: **{tx_count}**")

            if st.button(f"🗑 Delete {base}", key=base):
                try:
                    os.remove(yaml_path)
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                    st.success(f"Deleted {base}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete {base}: {e}")
        except Exception as e:
            st.warning(f"Could not load {yaml_name}: {e}")

# === Upload to Google Drive ===
st.markdown("---")
st.subheader("📤 Upload Evidence to Google Drive")

with st.form("admin_drive_upload"):
    uploaded_file = st.file_uploader("Upload a YAML or PDF file", type=["yaml", "pdf"])
    submit = st.form_submit_button("Upload")

    if submit:
        if uploaded_file is None:
            st.error("No file selected.")
        else:
            os.makedirs("temp", exist_ok=True)
            temp_path = os.path.join("temp", uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            try:
                file_id = upload_to_drive(temp_path)
                st.success(f"Uploaded to Drive (ID: {file_id})")
            except Exception as e:
                st.error(f"Upload failed: {e}")

            os.remove(temp_path)

# === Sync from Google Drive ===
st.markdown("---")
st.subheader("🔄 Sync Evidence from Google Drive")

if st.button("Sync now"):
    synced = sync_drive_to_local()
    if synced:
        st.success(f"Synced {len(synced)} new files from Drive.")
    else:
        st.info("All files are already synced.")
