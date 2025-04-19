import streamlit as st
from database_builder import build_database_from_zip  # or whatever your function is called

st.set_page_config(page_title="🔄 Rebuild SQLite Database", layout="centered")
st.title("🔄 Rebuild SQLite Database")
st.write("""
This will ingest all of your YAMLs and CSVs and produce a fresh
`data/hawaii.db` for the map and reports.
""")

if st.button("Rebuild now"):
    with st.spinner("Rebuilding database…"):
        try:
            path = build_database_from_zip()  # make sure this returns the path, or ignore its return
            st.success(f"✅ New DB created at `{path}`")
        except Exception as e:
            st.error(f"⚠️ Rebuild failed: {e}")
