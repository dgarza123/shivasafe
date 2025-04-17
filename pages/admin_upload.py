import os
import streamlit as st
import yaml
import pandas as pd
import importlib.util
import shutil

EVIDENCE_DIR = "evidence"
DATA_PATH = "data/hawaii.db"

st.set_page_config(page_title="Admin: Upload YAMLs + Rebuild", layout="centered")
st.title("📤 Upload YAML Evidence Files (No ZIP Required)")

# Cleanup toggle
if st.button("🧹 Clear all YAMLs in /evidence"):
    if os.path.exists(EVIDENCE_DIR):
        for root, _, files in os.walk(EVIDENCE_DIR):
            for file in files:
                if file.lower().endswith(".yaml"):
                    os.remove(os.path.join(root, file))
    st.success("✅ Cleared old YAMLs from /evidence")

# File uploader (multiple YAMLs)
uploaded_files = st.file_uploader("📄 Upload .yaml files directly (up to 100)", type="yaml", accept_multiple_files=True)

if uploaded_files:
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    saved_files = []

    for file in uploaded_files:
        file_path = os.path.join(EVIDENCE_DIR, file.name)
        with open(file_path, "wb") as out:
            out.write(file.read())
        saved_files.append(file_path)

    st.success(f"✅ Uploaded {len(saved_files)} YAML file(s) to /evidence")

    # Begin validation
    st.subheader("🔍 Validation Summary")
    results = []

    required_top_fields = ["certificate_number", "document", "transactions"]
    required_tx_fields = ["grantor", "grantee", "parcel_id"]

    for path in saved_files:
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except Exception as e:
                results.append({
                    "file": os.path.relpath(path),
                    "status": "❌ INVALID YAML",
                    "problem": f"YAML parse error: {str(e)}"
                })
                continue

        for key in required_top_fields:
            if key not in data:
                results.append({
                    "file": os.path.relpath(path),
                    "status": "⚠️ MISSING FIELD",
                    "problem": f"Top-level key missing: {key}"
                })

        tx_list = data.get("transactions", [])
        if not isinstance(tx_list, list) or len(tx_list) == 0:
            results.append({
                "file": os.path.relpath(path),
                "status": "⚠️ NO TRANSACTIONS",
                "problem": "transactions key is missing, empty, or not a list"
            })
            continue

        for i, tx in enumerate(tx_list):
            for f in required_tx_fields:
                if f not in tx:
                    results.append({
                        "file": os.path.relpath(path),
                        "status": "⚠️ MISSING TX FIELD",
                        "problem": f"Missing '{f}' in transaction #{i + 1}"
                    })

    df = pd.DataFrame(results)

    if df.empty:
        st.success("✅ All uploaded files passed validation.")
    else:
        st.warning(f"⚠️ {len(df)} issue(s) found.")
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇️ Download Validation Report", data=df.to_csv(index=False), file_name="yaml_validation_issues.csv", mime="text/csv")

    # Optional rebuild button
    if st.button("🔧 Rebuild hawaii.db from /evidence"):
        try:
            script_path = os.path.join("scripts", "rebuild_db_from_yaml.py")
            spec = importlib.util.spec_from_file_location("rebuild_db", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            with st.spinner("Rebuilding database..."):
                count = module.build_db()

            st.success(f"✅ Rebuild complete: {count} transaction row(s) inserted into hawaii.db")

            # Preview
            import sqlite3
            conn = sqlite3.connect(DATA_PATH)
            df = pd.read_sql_query("SELECT * FROM parcels LIMIT 10", conn)
            conn.close()
            st.subheader("📄 Sample from Rebuilt Database:")
            st.dataframe(df)

        except Exception as e:
            st.error(f"❌ Rebuild failed: {e}")
