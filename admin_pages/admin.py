import streamlit as st
import os
import yaml
from datetime import datetime

st.set_page_config(page_title="Admin Tools", layout="wide")
st.title("Admin Control Panel")

# Load password
CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
ADMIN_PASSWORD = config.get("admin_password")

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    pw = st.text_input("Enter admin password:", type="password")
    if pw == ADMIN_PASSWORD:
        st.session_state.admin_logged_in = True
        st.rerun()
    else:
        st.stop()

st.success("Access granted.")

# === Links to Admin Tools ===
st.subheader("Quick Access")
st.markdown("- [Upload Evidence](upload)")
st.markdown("- [Fix YAML Structure](fix_yaml)")
st.markdown("- [Return to Viewer](timeline)")

# === Embedded Uploader to Root ===
st.markdown("---")
st.subheader("Upload Any File to App Root")

with st.form("upload_root_inline"):
    uploaded = st.file_uploader("Select a file to upload to the root directory", type=None)
    submit = st.form_submit_button("Upload")

    if submit and uploaded:
        try:
            save_path = os.path.join(".", uploaded.name)
            with open(save_path, "wb") as f:
                f.write(uploaded.read())
            st.success(f"Uploaded to: {uploaded.name}")
        except Exception as e:
            st.error(f"Upload failed: {e}")

# === File Deletion Section ===
st.markdown("---")
st.subheader("Delete Uploaded Evidence")

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)
yaml_files = sorted([f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml")])

if not yaml_files:
    st.info("No YAML evidence files found.")
    st.stop()

for yaml_name in yaml_files:
    base = yaml_name.replace("_entities.yaml", "")
    yaml_path = os.path.join(EVIDENCE_DIR, yaml_name)
    pdf_path = os.path.join(EVIDENCE_DIR, base + ".pdf")

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        tx_count = len(data.get("transactions", []))
        mod_time = datetime.fromtimestamp(os.path.getmtime(yaml_path)).strftime('%Y-%m-%d %H:%M:%S')

        st.markdown(f"### {base}")
        st.caption(f"Last Modified: {mod_time}")
        st.markdown(f"- Transactions: {tx_count}")

        if st.button(f"Delete {base}", key=base):
            try:
                os.remove(yaml_path)
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                st.success(f"Deleted {base}")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete {base}: {e}")
    except Exception as e:
        st.warning(f"Error reading {yaml_name}: {e}")
