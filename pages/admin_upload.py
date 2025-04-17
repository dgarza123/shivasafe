import os
import streamlit as st
import zipfile
import importlib.util
import pandas as pd
import sqlite3

st.set_page_config(page_title="Admin: Upload & Rebuild", layout="centered")
st.title("🛠️ Upload YAML ZIP and Rebuild hawaii.db")

uploaded_file = st.file_uploader("📦 Upload a ZIP with nested folders of YAMLs", type="zip")

if uploaded_file:
    os.makedirs("upload", exist_ok=True)
    zip_path = os.path.join("upload", "yamls.zip")

    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ ZIP uploaded")

    extract_to = "evidence"
    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    st.info("📂 ZIP extracted (with folders) to /evidence")

    # Run rebuild script
    try:
        script_path = os.path.join("scripts", "rebuild_db_from_yaml.py")
        spec = importlib.util.spec_from_file_location("rebuild_db", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with st.spinner("🔧 Rebuilding database..."):
            count = module.build_db()

        st.success(f"🎉 Database rebuilt with {count} transactions")

        # Show preview
        conn = sqlite3.connect("data/hawaii.db")
        df = pd.read_sql_query("SELECT * FROM parcels LIMIT 10", conn)
        conn.close()
        st.subheader("📄 Preview of parsed transactions:")
        st.dataframe(df)

    except Exception as e:
        st.error(f"⚠️ Failed to rebuild DB: {e}")
