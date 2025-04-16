import os
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Upload Database", layout="centered")
st.title("📁 Upload a New hawaii.db")

# Access control (simple)
password = st.text_input("Admin Password", type="password")
if password != st.secrets.get("admin_password", "changeme"):
    st.warning("Enter admin password to continue")
    st.stop()

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "hawaii.db")
os.makedirs(DB_DIR, exist_ok=True)

# Upload form
with st.form("upload_db"):
    db_file = st.file_uploader("Upload hawaii.db (SQLite file)", type=["db"])
    submitted = st.form_submit_button("Upload and Replace")

if submitted:
    if db_file is None:
        st.error("Please upload a .db file.")
        st.stop()

    # Save uploaded file
    with open(DB_PATH, "wb") as f:
        f.write(db_file.read())
    st.success(f"✅ Database saved to {DB_PATH}")

    # Validate structure
    try:
        conn = sqlite3.connect(DB_PATH)
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
        if "parcels" not in tables["name"].values:
            st.error("❌ 'parcels' table not found. This is not a valid hawaii.db file.")
        else:
            count = pd.read_sql_query("SELECT COUNT(*) as n FROM parcels", conn)["n"].iloc[0]
            st.success(f"📦 parcels table found with {count} records.")
        conn.close()
    except Exception as e:
        st.error(f"❌ Failed to open database: {e}")
