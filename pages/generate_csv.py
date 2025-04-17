import streamlit as st
import os
import subprocess
import pandas as pd

st.set_page_config(page_title="Generate Hawaii.csv", layout="centered")
st.title("🧮 Generate `Hawaii.csv` from hawaii.db + TMK files")

st.markdown("""
This tool will:
- Load all TMKs from `hawaii.db`
- Merge coordinates from all available `.csv` files
- Compute suppression status (2015–2025)
- Export to `Hawaii.csv` in the project root
""")

if st.button("⚙️ Run generate_hawaii_csv.py"):
    try:
        result = subprocess.run(
            ["python", "scripts/generate_hawaii_csv.py"],
            capture_output=True, text=True, check=True
        )
        st.success("✅ Hawaii.csv generated successfully.")
        st.code(result.stdout)
    except subprocess.CalledProcessError as e:
        st.error("❌ Script failed.")
        st.code(e.stderr)

# Preview and download if exists
if os.path.exists("Hawaii.csv"):
    df = pd.read_csv("Hawaii.csv")
    st.markdown(f"### 🧾 Preview of Hawaii.csv ({len(df)} parcels)")
    st.dataframe(df.head(100))
    st.download_button("⬇️ Download Hawaii.csv", df.to_csv(index=False), "Hawaii.csv", "text/csv")
