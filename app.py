import streamlit as st
import yaml
import os
from io import StringIO
import base64
import hashlib
from pathlib import Path

# Set up global app config
st.set_page_config(page_title="Forensic Document Intelligence Portal", layout="wide")
st.title("📁 Forensic Document Intelligence Portal")
st.markdown("Upload forensic YAML evidence to explore entities, transactions, parcels, and patterns.")

# Initialize session state
if "yaml_data" not in st.session_state:
    st.session_state.yaml_data = []

# Sidebar Navigation
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Transactions", "Entities", "Timeline", "DLNR Checker", "Report Builder"])

# Upload Forensic YAMLs
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Upload YAML Files")
uploaded_files = st.sidebar.file_uploader("Upload .yaml forensic outputs", type=["yaml", "yml"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            raw_text = uploaded_file.read().decode("utf-8")
            parsed_yaml = yaml.safe_load(StringIO(raw_text))

            # SHA256 validation
            file_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            parsed_yaml["_uploaded_filename"] = uploaded_file.name
            parsed_yaml["_sha256"] = file_hash

            st.session_state.yaml_data.append(parsed_yaml)

        except Exception as e:
            st.error(f"❌ Failed to parse {uploaded_file.name}: {e}")

# Route to appropriate pages
if page == "Home":
    if not st.session_state.yaml_data:
        st.info("Upload one or more forensic YAML files to begin analysis.")
    else:
        st.success("✅ YAML files loaded and ready.")
        st.write("Explore cross-linked transactions, flagged entities, escrow trails, and parcel status using the navigation panel.")

        st.subheader("Loaded Files:")
        for entry in st.session_state.yaml_data:
            st.markdown(f"- `{entry['_uploaded_filename']}` | SHA256: `{entry['_sha256'][:12]}...`")

elif page == "Transactions":
    st.switch_page("transactions_dashboard.py")

elif page == "Entities":
    st.switch_page("entity_viewer.py")

elif page == "Timeline":
    st.switch_page("timeline_view.py")

elif page == "DLNR Checker":
    st.switch_page("dlnr_checker.py")

elif page == "Report Builder":
    st.switch_page("report_builder.py")
