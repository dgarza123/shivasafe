import streamlit as st
from scripts.unzip_and_rebuild import unzip_yaml_bundle

st.title("🧩 Upload & Rebuild YAML Database")

uploaded_file = st.file_uploader("Upload your zipped YAML bundle", type="zip")

if uploaded_file:
    with open("upload/yamls.zip", "wb") as f:
        f.write(uploaded_file.read())
    st.success("ZIP uploaded successfully.")

    if st.button("⚙️ Unzip and Rebuild hawaii.db"):
        unzip_yaml_bundle("upload/yamls.zip")
        st.success("hawaii.db rebuilt from uploaded YAMLs ✅")
