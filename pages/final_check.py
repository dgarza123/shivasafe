# pages/final_check.py

import os
import sys

#  ─ Add project root to Python path so we can import root‑level modules ─────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# ─────────────────────────────────────────────────────────────────────────────────

import streamlit as st
from sqlite3 import OperationalError
from database_builder import build_database

st.title("🔄 Rebuild SQLite Database")

st.write(
    """
    Click the button below to delete and rebuild `data/hawaii.db` from your
    CSVs and YAMLs. Any errors will show up here.
    """
)

if st.button("Rebuild Now"):
    try:
        build_database()
        st.success("✅ Database successfully rebuilt!")
    except FileNotFoundError as e:
        st.error(f"Couldn’t find a data file: {e}")
    except OperationalError as e:
        st.error(f"SQLite error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
