import streamlit as st
import os
import yaml

st.set_page_config(page_title="Admin Manager", layout="wide")
st.title("Manage Uploaded Evidence")

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

all_files = sorted(os.listdir(EVIDENCE_DIR))
yaml_files = [f for f in all_files if f.endswith("_entities.yaml")]

if not yaml_files:
    st.info("No evidence files found.")
    st.stop()

for fname in yaml_files:
    base = fname.replace("_entities.yaml", "")
    pdf_path = os.path.join(EVIDENCE_DIR, base + ".pdf")
    yaml_path = os.path.join(EVIDENCE_DIR, fname)

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        doc = data.get("document", base + ".pdf")
        tx_count = len(data.get("transactions", []))
        st.markdown(f"#### 📄 `{doc}` | {tx_count} transactions")
        st.markdown(f"- YAML: `{fname}`")
        st.markdown(f"- PDF: `{base}.pdf`")

        if st.button(f"🗑 Delete `{base}`", key=fname):
            os.remove(yaml_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            st.success(f"Deleted `{base}`")
            st.experimental_rerun()
    except Exception as e:
        st.warning(f"Could not load {fname}: {e}")
