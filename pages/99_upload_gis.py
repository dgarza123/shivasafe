import streamlit as st
import os

st.set_page_config(page_title="Upload GIS Files", layout="centered")
st.title("📁 Upload GIS Files to /data")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

st.markdown("Upload the three required TMK files:")
st.markdown("- `Hawaii2018.csv`\n- `Hawaii2022.csv`\n- `Hawaii2025.csv`")

uploaded_files = st.file_uploader("Choose CSV files", type="csv", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_path = os.path.join(DATA_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Uploaded: {uploaded_file.name}")

    st.info("Now you can rerun the suppression timeline script.")
