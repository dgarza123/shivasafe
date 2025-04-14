import streamlit as st
import os
import yaml

# Load password from config.yaml
CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
ADMIN_PASSWORD = config.get("admin_password")
if not ADMIN_PASSWORD:
    st.error("Admin password missing in config.yaml")
    st.stop()

st.set_page_config(page_title="ShivaSafe File Manager", layout="wide")
st.title("🗂️ Evidence File Manager")

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

# File list
all_files = os.listdir(TMP_DIR)
yaml_files = sorted([f for f in all_files if f.endswith("_entities.yaml")], reverse=True)

if not yaml_files:
    st.info("No uploaded evidence files found.")
    st.stop()

st.markdown("### Uploaded Case Files")
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
    except:
        doc = base
        sha = "—"
        created = "—"
        tx_count = 0

    cols = st.columns([2, 2, 2, 2, 1])
    cols[0].markdown(f"📄 **{doc}**")
    cols[1].markdown(f"🕓 `{created}`")
    cols[2].markdown(f"🔢 `{tx_count} tx`")
    cols[3].markdown(f"🔑 `{sha}`")
    if cols[4].button("🗑️ Delete", key=fname):
        try:
            os.remove(yaml_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            st.success(f"Deleted `{doc}`")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to delete `{doc}`: {e}")
