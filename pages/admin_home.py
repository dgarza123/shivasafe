import streamlit as st
import os
import yaml
from datetime import datetime
from login_manager import current_role

# 🔐 Restrict to editors
if current_role() != "editor":
    st.stop()

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("🛠 ShivaSafe Admin Panel")

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# === Upload Evidence ===
st.subheader("📤 Upload YAML or PDF")

with st.form("local_upload_form"):
    uploaded_file = st.file_uploader("Choose a YAML or PDF file", type=["yaml", "pdf"])
    submit = st.form_submit_button("Upload")

    if submit:
        if uploaded_file is None:
            st.warning("Please select a file to upload.")
        else:
            save_path = os.path.join(EVIDENCE_DIR, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.read())
            st.success(f"✅ Saved to `/evidence/` as `{uploaded_file.name}`")
            st.rerun()

# === Manage Files ===
st.markdown("---")
st.subheader("📂 Current Evidence Files")

yaml_files = sorted(f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml"))

if not yaml_files:
    st.info("No YAML evidence files found.")
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
            st.caption(f"🕒 Last Modified: {mod_time}")
            st.markdown(f"- SHA256: `{sha}`")
            st.markdown(f"- Transactions: **{tx_count}**")
            st.markdown(f"- PDF Present: {'✅' if os.path.exists(pdf_path) else '❌'}")

            if st.button(f"🗑 Delete `{base}`", key=f"del_{base}"):
                try:
                    os.remove(yaml_path)
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                    st.success(f"Deleted `{base}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete: {e}")
        except Exception as e:
            st.warning(f"⚠️ Could not read `{yaml_name}`: {e}")
