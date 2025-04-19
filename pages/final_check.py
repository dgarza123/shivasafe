# pages/final_check.py

import streamlit as st
from sqlite3 import OperationalError
from database_builder import build_database

st.title("🔄 Rebuild SQLite Database")

if st.button("Rebuild Now"):
    try:
        build_database()
        st.success("✅ Database successfully rebuilt!")
    except OperationalError as e:
        st.error(f"Database error: {e}")
    except FileNotFoundError as e:
        st.error(f"Couldn’t find data file: {e}")
