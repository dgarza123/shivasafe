# pages/admin_uploader.py

import os
import sys
import subprocess
import streamlit as st

#  ───  ensure repo root is on PYTHONPATH  ─────────────────────────────────────────────
#  Streamlit's cwd is your repo root, but just in case:
ROOT = os.path.abspath(os.getcwd())
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

#  ───  import your rebuild functions  ────────────────────────────────────────────────
try:
    from ingest_yaml_to_db import rebuild_db_from_zip
except ImportError:
    rebuild_db_from_zip = None

try:
    from rebuild_db import rebuild_sqlite
except ImportError:
    rebuild_sqlite = None

st.set_page_config(page_title="Admin Uploader", layout="wide")
st.title("📂 Admin: Upload & Rebuild")

DATA_DIR = "data"
EVIDENCE_DIR = "evidence"
DB_PATH = os.path.join(DATA_DIR, "hawaii.db")

# ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

st.markdown("### 1) Upload CSVs → `/data`")
uploaded_csvs = st.file_uploader(
    "Choose CSV files", type="csv", accept_multiple_files=True
)
if uploaded_csvs:
    for up in uploaded_csvs:
        dest = os.path.join(DATA_DIR, up.name)
        with open(dest, "wb") as f:
            f.write(up.getbuffer())
        st.success(f"✅ `{up.name}` → `{dest}`")

st.markdown("### 2) Upload YAMLs → `/evidence`")
uploaded_yamls = st.file_uploader(
    "Choose YAML files", type=("yaml","yml"), accept_multiple_files=True
)
if uploaded_yamls:
    for up in uploaded_yamls:
        dest = os.path.join(EVIDENCE_DIR, up.name)
        with open(dest, "wb") as f:
            f.write(up.getbuffer())
        st.success(f"✅ `{up.name}` → `{dest}`")

st.markdown("### 3) Rebuild the SQLite Database")
if st.button("🔄 Rebuild DB"):
    try:
        # 1) ingest YAMLs
        if rebuild_db_from_zip:
            rebuild_db_from_zip(zip_path=None, out_db=DB_PATH)
        else:
            # fallback to script
            proc = subprocess.run(
                ["python", "scripts/rebuild_db_from_yaml.py", "--out-db", DB_PATH],
                capture_output=True, text=True
            )
            if proc.returncode:
                raise RuntimeError(proc.stderr)

        # 2) load CSVs / patch anything
        if rebuild_sqlite:
            rebuild_sqlite(DB_PATH)
        else:
            proc = subprocess.run(
                ["python", "rebuild_db.py", "--db", DB_PATH],
                capture_output=True, text=True
            )
            if proc.returncode:
                raise RuntimeError(proc.stderr)

        st.success("🏗️ Database rebuilt successfully!")
    except Exception as e:
        st.error(f"🔴 Rebuild failed:\n```\n{e}\n```")
