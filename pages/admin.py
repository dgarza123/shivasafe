import streamlit as st
import os

st.set_page_config(page_title="Admin File Manager", layout="wide")
st.title("Admin: Evidence File Viewer")

EVIDENCE_DIR = "evidence"

def list_pairs():
    files = os.listdir(EVIDENCE_DIR)
    yaml_files = sorted(f for f in files if f.endswith("_entities.yaml"))
    entries = []
    for y in yaml_files:
        base = y.replace("_entities.yaml", "")
        pdf = base + ".pdf"
        entries.append((pdf, y, os.path.exists(os.path.join(EVIDENCE_DIR, pdf))))
    return entries

st.markdown("### Current Evidence")

for pdf, yml, has_pdf in list_pairs():
    st.markdown(f"- **YAML:** `{yml}`")
    if has_pdf:
        st.markdown(f"  - **PDF:** `{pdf}` (linked)")
    else:
        st.markdown(f"  - **Missing PDF:** `{pdf}`")
    st.markdown("---")