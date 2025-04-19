# pages/upload_data.py

import streamlit as st
import os

st.title("📂 Upload CSV & YAML Data")

st.markdown("""
Use this uploader to send your parcel CSVs (Hawaii2020.csv, …, gps_patch.csv, etc.)  
and your evidence YAMLs up to the server.  
- **CSV** files go into `data/`  
- **YAML** files go into `evidence/`  
Once you’ve uploaded everything, visit **Rebuild SQLite Database** to re‑ingest.
""")

uploaded = st.file_uploader(
    "Select one or more CSV or YAML files",
    type=["csv", "yaml", "yml"],
    accept_multiple_files=True,
)

if uploaded:
    for up in uploaded:
        ext = up.name.split(".")[-1].lower()
        if ext == "csv":
            folder = "data"
        elif ext in ("yaml", "yml"):
            folder = "evidence"
        else:
            st.warning(f"Skipping unsupported file type: {up.name}")
            continue

        os.makedirs(folder, exist_ok=True)
        save_path = os.path.join(folder, up.name)
        with open(save_path, "wb") as f:
            f.write(up.getbuffer())
        st.success(f"✔️  Saved `{up.name}` → `{folder}/`")
