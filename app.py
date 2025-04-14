import streamlit as st
import hashlib
import os
import json
import yaml

from modules.decode_controller import run_full_decode
from modules.entity_extraction import extract_entities
from modules.registry_scanner import extract_registry_keys
from modules.suppression_detector import flag_suppressed_blocks

st.set_page_config(layout="wide")
st.title("🧾 ShivaSafe Forensic PDF Decoder")

# === Upload
uploaded_files = st.file_uploader("Upload one or more PDF containers", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.markdown("### 🔍 Uploaded Files")
    for file in uploaded_files:
        file_bytes = file.read()
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        filename = file.name

        # Save to /tmp
        tmp_path = f"/tmp/{sha256}.pdf"
        with open(tmp_path, "wb") as f:
            f.write(file_bytes)

        # Process
        st.info(f"📄 Processing `{filename}` …")
        decoded_blocks = run_full_decode(file_bytes)

        # Registry keys + entity extraction
        entities = extract_entities(decoded_blocks)
        registry_keys = extract_registry_keys(decoded_blocks)
        flagged_blocks = flag_suppressed_blocks(decoded_blocks)

        # Save JSON/YAML output
        json_path = f"/tmp/{sha256}_blocks.json"
        yaml_path = f"/tmp/{sha256}_entities.yaml"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(decoded_blocks, f, indent=2)

        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump({"transactions": entities}, f, sort_keys=False)

        # Show success message and rerun
        st.success(f"✅ `{filename}` processed and saved.")
        st.experimental_rerun()
