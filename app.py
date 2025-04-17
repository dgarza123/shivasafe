# test_app.py
import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config("🧪 Database Test Page")
st.title("🧪 Test Parcel DB Table")

DB_PATH = "data/hawaii.db"

if not os.path.exists(DB_PATH):
    st.error("❌ hawaii.db not found in /data")
    st.stop()

try:
    conn = sqlite3.connect(DB_PATH)
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
    st.markdown("### 📋 Tables in DB:")
    st.dataframe(tables)

    if 'parcels' in tables['name'].values:
        df = pd.read_sql_query("PRAGMA table_info(parcels)", conn)
        st.markdown("### 🧬 Schema for 'parcels' Table")
        st.dataframe(df)

        st.markdown("### 🧪 Sample Records")
        sample = pd.read_sql_query("SELECT * FROM parcels LIMIT 5", conn)
        st.dataframe(sample)
    else:
        st.warning("❌ 'parcels' table not found in hawaii.db")

    conn.close()
except Exception as e:
    st.error(f"❌ Failed to load database: {e}")
