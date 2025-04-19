import os
import sys

# make sure the repo root is on sys.path so
# `import database_builder` always works
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st
from database_builder import build_database_from_zip

# ---- on first run, (re)build your SQLite DB if missing ----
DB_PATH = os.path.join("data", "hawaii.db")
if not os.path.exists(DB_PATH):
    st.sidebar.info("⏳ Building database…")
    # adjust these arguments to your zip / output path
    build_database_from_zip("evidence/yaml_zips.zip", DB_PATH)
    st.sidebar.success("✅ Database ready")

# ---- sidebar navigation ----
st.sidebar.title("📑 Pages")
page = st.sidebar.radio("", [
    "Home",
    "Upload Evidence",
    "Map Viewer",
    "TMK Checker",
])

# ---- page dispatcher ----
if page == "Home":
    st.title("🏠 Welcome to Shivasafe")
    st.write("Use the sidebar to pick a page.")

elif page == "Upload Evidence":
    from pages.evidence_uploader import run as run_uploader
    run_uploader()

elif page == "Map Viewer":
    from pages.map_viewer import run as run_map
    run_map()

elif page == "TMK Checker":
    from pages.tmk_checker import run as run_checker
    run_checker()
