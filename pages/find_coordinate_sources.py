import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="Find TMK Coordinate Sources", layout="wide")
st.title("🧭 TMK → Coordinate Source Scanner")

ROOT_DIRS = [".", "data", "evidence", "suppression", "resources"]

found = []

def is_valid_coord_file(df):
    cols = [c.lower() for c in df.columns]
    return (
        any(c in cols for c in ["tmk", "parcel_id"]) and
        any(c in cols for c in ["lat", "latitude"]) and
        any(c in cols for c in ["lon", "longitude"])
    )

for dir_path in ROOT_DIRS:
    if not os.path.isdir(dir_path):
        continue
    for fname in os.listdir(dir_path):
        if not fname.endswith(".csv"):
            continue
        full_path = os.path.join(dir_path, fname)
        try:
            df = pd.read_csv(full_path, nrows=1000)
            if is_valid_coord_file(df):
                found.append((full_path, len(df), df.head(5)))
        except Exception as e:
            st.warning(f"⚠️ Skipped {fname}: {e}")

if not found:
    st.error("❌ No coordinate-containing TMK CSVs found in scanned folders.")
else:
    st.success(f"✅ Found {len(found)} usable coordinate files:")
    for path, count, sample in found:
        st.markdown(f"### 📄 {path} — {count} rows")
        st.dataframe(sample)
