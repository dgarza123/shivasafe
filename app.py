import streamlit as st
from create_db import write_db_if_missing
write_db_if_missing()

st.set_page_config(
    page_title="ShivaSafe: Parcel Trail Viewer",
    layout="wide",
)

# --- HEADER ---
st.title("ShivaSafe")
st.markdown("""
### Land Title Suppression Analysis

View known land transactions extracted from notarized PDFs and cross-check parcel status across 2018, 2022, and 2025 records.
""")

# --- FILE COUNT / STATUS ---
st.markdown("---")
st.subheader("Quick Stats")

from pathlib import Path
import sqlite3

db_path = Path("data/hawaii.db")
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    row = cursor.execute("SELECT COUNT(*) FROM parcels").fetchone()
    st.success(f"📄 `{row[0]}` verified transactions loaded.")
    conn.close()
else:
    st.warning("hawaii.db not found.")

# --- NAVIGATION ---
st.markdown("---")
st.subheader("Navigation")
st.markdown("""
- 📍 [Parcel Trail](pages/parcel_trail.py)
- 🗺️ [Suppression Map Viewer](pages/map_compare.py)
- 🧾 More analysis coming soon...
""")

st.markdown("---")
st.caption("Forensic analysis powered by Shiva PDF Analyzer")
