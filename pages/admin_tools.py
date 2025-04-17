import streamlit as st
import os
from scripts.unzip_and_rebuild import unzip_yaml_bundle

st.set_page_config(page_title="Admin Tools", layout="centered")
st.title("🔧 Admin Tools — Upload & Rebuild YAML Database")

st.markdown("""
Upload a `.zip` file containing your `*_entities.yaml` files.  
This will extract them into `/evidence/` and rebuild `hawaii.db` with:
- Suppression columns (2015, 2018, 2022, 2025)
- Grantee, amount, parcel ID, date
- Certificate ID + SHA256
""")

uploaded_file = st.file_uploader("📁 Upload zipped YAML files", type="zip")

if uploaded_file:
    os.makedirs("upload", exist_ok=True)
    zip_path = os.path.join("upload", "yamls.zip")

    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ ZIP file uploaded successfully.")

    if st.button("⚙️ Rebuild hawaii.db now"):
        unzip_yaml_bundle(zip_path)
        st.success("🎉 Database rebuilt and YAMLs unpacked into /evidence/")
