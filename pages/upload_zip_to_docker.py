import os
import streamlit as st

st.set_page_config(page_title="Upload YAML ZIP", layout="centered")
st.title("📦 Upload ZIP of YAMLs to /upload")

uploaded_file = st.file_uploader("Choose your yamls.zip file", type="zip")

if uploaded_file:
    os.makedirs("upload", exist_ok=True)
    save_path = os.path.join("upload", "yamls.zip")

    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ yamls.zip uploaded to /upload/yamls.zip")
