import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="🛠 TMK Timeline Debug", layout="wide")
st.title("🧪 TMK Suppression Timeline Debugger")

folder = "data"
files = ["Hawaii2018.csv", "Hawaii2022.csv", "Hawaii2025.csv"]

for fname in files:
    st.markdown(f"### 📄 `{fname}`")
    path = os.path.join(folder, fname)

    if not os.path.exists(path):
        st.error("❌ File not found.")
        continue

    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()

        st.write("✅ Columns:", df.columns.tolist())

        if "TMK" not in df.columns:
            st.error("❌ 'TMK' column is missing.")
            continue

        df["TMK"] = df["TMK"].astype(str).str.strip()
        st.write("🔢 First 5 TMK values:", df["TMK"].head().tolist())
        st.write("📊 Total rows:", len(df))
        st.write("🔁 Unique TMKs:", df["TMK"].nunique())
        st.write("🚫 Blank or null TMKs:", df["TMK"].isnull().sum() + (df["TMK"] == "").sum())

    except Exception as e:
        st.error(f"❌ Failed to read {fname}: {e}")
