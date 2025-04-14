import streamlit as st
import os

st.set_page_config(page_title="Admin File Manager", layout="wide")
st.title("Admin: Evidence File Manager")

EVIDENCE_DIR = "evidence"

def list_pairs():
    files = os.listdir(EVIDENCE_DIR)
    yaml_files = sorted(f for f in files if f.endswith("_entities.yaml"))
    entries = []
    for yml in yaml_files:
        base = yml.replace("_entities.yaml", "")
        pdf = base + ".pdf"
        pdf_path = os.path.join(EVIDENCE_DIR, pdf)
        yml_path = os.path.join(EVIDENCE_DIR, yml)
        entries.append({
            "base": base,
            "pdf": pdf,
            "yml": yml,
            "pdf_exists": os.path.exists(pdf_path),
            "pdf_path": pdf_path,
            "yml_path": yml_path,
        })
    return entries

cases = list_pairs()

if not cases:
    st.info("No evidence files found.")
    st.stop()

for entry in cases:
    st.markdown(f"### `{entry['yml']}`")
    if entry["pdf_exists"]:
        st.markdown(f"- PDF: `{entry['pdf']}`")
    else:
        st.markdown(f"- PDF: ❌ Missing")

    with st.expander("Delete This Case?"):
        if st.button(f"🗑️ Delete `{entry['base']}`", key=entry['base']):
            try:
                os.remove(entry["yml_path"])
                if entry["pdf_exists"]:
                    os.remove(entry["pdf_path"])
                st.success(f"Deleted `{entry['base']}`")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error deleting files: {e}")
    st.markdown("---")