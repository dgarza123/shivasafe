# pages/rebuild_db.py

import os, streamlit as st
from database_builder import build_database_from_zip

st.title("🔄 Rebuild SQLite Database")

# default paths relative to your project root
zip_default = st.text_input("Zip file path:", "evidence_and_data.zip")
db_default  = st.text_input("Output DB path:",   "data/hawaii.db")

if st.button("Rebuild"):
    try:
        build_database_from_zip(zip_default, db_default)
        st.success(f"✓ Database rebuilt at `{db_default}`")
    except Exception as e:
        st.error(f"Rebuild failed: {e}")
