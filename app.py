import streamlit as st
import yaml
import os
from io import StringIO
import hashlib
from pathlib import Path
from file_storage import save_uploaded_pair, list_saved_cases

st.set_page_config(page_title="Forensic Document Intelligence Portal", layout="wide")
st.title("📁 Forensic Document Intelligence Portal")
st.markdown("Upload forensic YAML + PDF pairs to explore entities, transactions, parcels, and patterns.")

# Initialize session state
if "yaml_data" not in st.session_state:
    st.session_state.yaml_data = list_saved_cases()

# Upload Forensic YAML + PDF
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Upload YAML + PDF")
yaml_file = st.sidebar.file_uploader("YAML file", type=["yaml", "yml"], key="yaml_upload")
pdf_file = st.sidebar.file_uploader("Matching PDF file", type="pdf", key="pdf_upload")

if yaml_file and pdf_file:
    if st.sidebar.button("Save Evidence"):
        try:
            parsed_yaml = save_uploaded_pair(yaml_file, pdf_file)
            st.session_state.yaml_data.append(parsed_yaml)
            st.sidebar.success(f"✅ Saved: {yaml_file.name} + {pdf_file.name}")
        except Exception as e:
            st.sidebar.error(f"❌ Upload failed: {e}")

# Display Home content
if not st.session_state.yaml_data:
    st.info("Upload YAML + PDF pairs to begin analysis.")
else:
    st.success("✅ Cases loaded from evidence folder.")
    st.write("Explore cross-linked transactions, flagged entities, escrow trails, and parcel status using the top-left Pages navigation panel.")

    st.subheader("Loaded Cases:")
    for entry in st.session_state.yaml_data:
        link = entry.get("_pdf_path")
        st.markdown(f"- `{entry['_uploaded_filename']}` | SHA256: `{entry['_sha256'][:12]}...` [📄 View PDF]({link})")
