import streamlit as st
import os
import yaml

st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("Evidence File Manager")

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

yaml_files = [f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml")]

if not yaml_files:
    st.info("No YAML files in evidence folder.")
    st.stop()

for yaml_name in sorted(yaml_files):
    base = yaml_name.replace("_entities.yaml", "")
    pdf_path = os.path.join(EVIDENCE_DIR, base + ".pdf")
    yaml_path = os.path.join(EVIDENCE_DIR, yaml_name)

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        tx_count = len(data.get("transactions", []))
        st.markdown(f"### 📄 `{base}` | {tx_count} transactions")

        if st.button(f"🗑 Delete `{base}`", key=base):
            os.remove(yaml_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            st.success(f"Deleted {base}")
            st.experimental_rerun()
    except Exception as e:
        st.warning(f"Error reading {yaml_name}: {e}")
