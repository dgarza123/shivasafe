import os
import streamlit as st
import zipfile
import importlib.util
import pandas as pd
import sqlite3

st.set_page_config(page_title="Admin: Upload & Rebuild", layout="centered")
st.title("🛠️ Upload YAML ZIP and Rebuild hawaii.db")

uploaded_file = st.file_uploader("📦 Upload a ZIP with one or more YAML files (in folders is OK)", type="zip")

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
    st.info("📂 ZIP extracted to /evidence (with folder support)")

    # 🔍 Diagnostic: show YAMLs found
    yaml_files = []
    for root, _, files in os.walk(extract_to):
        for file in files:
            if file.lower().endswith(".yaml"):
                yaml_files.append(os.path.join(root, file))

    if not yaml_files:
        st.error("❌ No .yaml files found. Check ZIP structure.")
        st.stop()
    else:
        st.success(f"✅ Found {len(yaml_files)} YAML file(s)")
        st.code('\n'.join(yaml_files))

    # Run rebuild script
    try:
        script_path = os.path.join("scripts", "rebuild_db_from_yaml.py")
        spec = importlib.util.spec_from_file_location("rebuild_db", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with st.spinner("🔧 Rebuilding database..."):
            count = module.build_db()

        st.success(f"🎉 Database rebuilt with {count} transaction row(s)")

        # Show preview
        conn = sqlite3.connect("data/hawaii.db")
        df = pd.read_sql_query("SELECT * FROM parcels LIMIT 10", conn)
        conn.close()
        st.subheader("📄 Sample of parsed transactions:")
        st.dataframe(df)

    except Exception as e:
        st.error(f"⚠️ Rebuild failed: {e}")
