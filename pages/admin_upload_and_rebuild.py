import os
import streamlit as st
import zipfile
import shutil
import importlib.util

st.set_page_config(page_title="Admin: Upload & Rebuild", layout="centered")
st.title("🛠️ Upload YAML ZIP and Rebuild hawaii.db")

# Upload ZIP file
uploaded_file = st.file_uploader("📦 Upload your yamls.zip", type="zip")

if uploaded_file:
    os.makedirs("upload", exist_ok=True)
    zip_path = os.path.join("upload", "yamls.zip")

    with open(zip_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ ZIP uploaded to /upload/yamls.zip")

    # Extract and clean
    extract_to = "evidence"
    os.makedirs(extract_to, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    # Flatten nested YAMLs
    for root, _, files in os.walk(extract_to):
        for file in files:
            if file.endswith(".yaml"):
                src = os.path.join(root, file)
                dst = os.path.join(extract_to, file)
                if src != dst:
                    shutil.move(src, dst)

    st.info("📂 YAMLs extracted to /evidence")

    # Dynamically import and run build_db
    try:
        script_path = os.path.join("scripts", "rebuild_db_from_yaml.py")
        spec = importlib.util.spec_from_file_location("rebuild_db", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.build_db()
        st.success("🎉 Database rebuilt successfully!")
    except Exception as e:
        st.error(f"⚠️ Failed to rebuild DB: {e}")
