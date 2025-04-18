import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CSV Cleaner", layout="centered")
st.title("🧹 Clean All CSV Files in Project")

ROOT_DIR = "."  # Start from root
csv_files = []

# Recursively gather all CSV files
for root, _, files in os.walk(ROOT_DIR):
    for file in files:
        if file.endswith(".csv") and "venv" not in root and "__pycache__" not in root:
            csv_files.append(os.path.join(root, file))

if not csv_files:
    st.warning("⚠️ No CSV files found in project.")
    st.stop()

st.info(f"🔍 Found {len(csv_files)} CSV files to scan.")

if st.button("🧼 Clean and Fix All CSV Files"):
    cleaned = 0
    failed = 0
    for path in csv_files:
        try:
            df = pd.read_csv(path, encoding="utf-8", engine="python")
        except Exception:
            try:
                df = pd.read_csv(path, encoding="utf-8-sig", engine="python")
            except Exception as e:
                st.error(f"❌ Failed to read {path}: {e}")
                failed += 1
                continue

        # Normalize headers
        df.columns = [col.strip().replace("\ufeff", "") for col in df.columns]

        # Strip whitespace in string cells
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.strip()

        # Save back
        try:
            df.to_csv(path, index=False, encoding="utf-8", line_terminator="\n")
            st.success(f"✅ Cleaned: {path}")
            cleaned += 1
        except Exception as e:
            st.error(f"❌ Failed to write {path}: {e}")
            failed += 1

    st.markdown("---")
    st.success(f"🎉 Done: {cleaned} cleaned, {failed} failed.")
