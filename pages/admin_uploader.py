# pages/admin_uploader.py
import os
import streamlit as st
from ingest_yaml_to_db import rebuild_db_from_zip
from rebuild_db import rebuild_sqlite

st.set_page_config(page_title="Admin Uploader", layout="wide")
st.title("📂 Upload Data & Evidence")

DATA_DIR = "data"
EVIDENCE_DIR = "evidence"
DB_PATH = "data/hawaii.db"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

st.markdown("## 1) Upload CSV files")
csv_files = st.file_uploader(
    "Select one or more CSVs to upload into `/data`", 
    type="csv", accept_multiple_files=True
)
if csv_files:
    for up in csv_files:
        dest = os.path.join(DATA_DIR, up.name)
        with open(dest, "wb") as f:
            f.write(up.getbuffer())
        st.success(f"Saved `{up.name}` → `{dest}`")

st.markdown("## 2) Upload YAML files")
yaml_files = st.file_uploader(
    "Select one or more YAMLs to upload into `/evidence`", 
    type=("yaml","yml"), accept_multiple_files=True
)
if yaml_files:
    for up in yaml_files:
        dest = os.path.join(EVIDENCE_DIR, up.name)
        with open(dest, "wb") as f:
            f.write(up.getbuffer())
        st.success(f"Saved `{up.name}` → `{dest}`")

st.markdown("## 3) Rebuild the database")
if st.button("🔄 Rebuild SQLite DB"):
    try:
        # first ingest YAMLs into new DB
        rebuild_db_from_zip(zip_path=None, out_db=DB_PATH)
        # then load CSVs / do any post‑processing
        rebuild_sqlite(DB_PATH)
        st.success("🏗️ Database rebuilt successfully!")
    except Exception as e:
        st.error(f"Rebuild failed:\n```\n{e}\n```")
