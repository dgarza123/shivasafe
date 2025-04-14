import streamlit as st
import os
import yaml
import zipfile
import io
import datetime

# Load admin password
CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
ADMIN_PASSWORD = config.get("admin_password")
if not ADMIN_PASSWORD:
    st.error("Admin password missing in config.yaml")
    st.stop()

st.set_page_config(page_title="Generate Evidence Bundle", layout="wide")
st.title("📦 Evidence Export")

TMP_DIR = "tmp"

# Auth
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

# Load YAMLs
yaml_files = sorted([f for f in os.listdir(TMP_DIR) if f.endswith("_entities.yaml")], reverse=True)

if not yaml_files:
    st.info("No uploaded YAML files found.")
    st.stop()

st.markdown("### Select files to package:")
selected_files = []

for fname in yaml_files:
    base = fname.replace("_entities.yaml", "")
    pdf_path = os.path.join(TMP_DIR, base + ".pdf")
    yaml_path = os.path.join(TMP_DIR, fname)

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        doc = data.get("document", base)
        sha = data.get("sha256", "")[:12]
        created = data.get("creation_date", "—")
        tx_count = len(data.get("transactions", []))
        label = f"{doc} | {created} | {tx_count} tx | SHA: {sha}"
        if st.checkbox(label, key=fname):
            selected_files.append((base, data))
    except Exception as e:
        st.warning(f"Could not load
