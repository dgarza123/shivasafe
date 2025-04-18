import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CSV Cleaner", layout="centered")
st.title("🧹 Clean All CSV Files in Project")

ROOT_DIR = "."
csv_files = []

for root, _, files in os.walk(ROOT_DIR):
    for file in files:
        if file.endswith(".csv") and "venv" not in root and "__pycache__" not in root:
            csv_files.append(os.path.join(root, file))

if not csv_files:
    st.warning("⚠️ No CSV files found.")
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

        # Check if CSV is blank
        if df.empty or len(df.columns) == 0:
            st.warning(f"⚠️ Skipped {path} (empty or no columns)")
            failed += 1
            continue

        # Clean headers
        df.columns = [col.strip().replace("\ufeff", "") for col in df.columns]

        # Clean string fields
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.strip()

        # Write cleaned file
        try:
            df.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")
            st.success(f"✅ Cleaned: {path}")
            cleaned += 1
        except Exception as e:
            st.error(f"❌ Failed to write {path}: {e}")
            failed += 1

    st.markdown("---")
    st.success(f"🎉 Done: {cleaned} cleaned, {failed} failed or skipped.")
