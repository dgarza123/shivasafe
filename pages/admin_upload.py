import os
import streamlit as st
import zipfile
import importlib.util
import pandas as pd
import sqlite3

st.set_page_config(page_title="Admin: Upload & Rebuild", layout="centered")
st.title("🛠️ Upload YAML ZIP and Rebuild hawaii.db")

uploaded_file = st.file_uploader("📦 Upload a ZIP containing your YAML files (folder nesting is OK)", type="zip")

if uploaded_file:
    # Save ZIP
    os.makedirs("upload", exist_ok=True)
    zip_path = os.path.join("upload", "yamls.zip")
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ ZIP uploaded")

    # Clean up previous evidence folder
    extract_to = "evidence"
    if os.path.exists(extract_to):
        for root, dirs, files in os.walk(extract_to):
            for file in files:
                if file.lower().endswith(".yaml"):
                    os.remove(os.path.join(root, file))
    else:
        os.makedirs(extract_to, exist_ok=True)
    st.warning("🧹 Cleared old YAMLs from /evidence")

    # Extract new ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    st.info("📂 Extracted new ZIP contents to /evidence")

    # Show found YAMLs for confirmation
    yaml_files = []
    for root, _, files in os.walk(extract_to):
        for file in files:
            if file.lower().endswith(".yaml"):
                yaml_files.append(os.path.join(root, file))

    if not yaml_files:
        st.error("❌ No .yaml files found after extraction. Check the ZIP format.")
        st.stop()
    else:
        st.success(f"✅ Found {len(yaml_files)} YAML file(s) in /evidence")
        st.code('\n'.join(yaml_files[:20]) + ("\n... (truncated)" if len(yaml_files) > 20 else ""))

    # Run database builder
    try:
        script_path = os.path.join("scripts", "rebuild_db_from_yaml.py")
        spec = importlib.util.spec_from_file_location("rebuild_db", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with st.spinner("🔧 Rebuilding hawaii.db from YAML files..."):
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
