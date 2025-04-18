import streamlit as st
import os

st.set_page_config(page_title="Admin: File Uploader", layout="centered")
st.title("🔼 Admin File Uploader")

st.markdown("""
Use this page to upload files directly into your project structure.

1. Select the **target folder** (root, data/, or scripts/).  
2. Choose one or more files from your local machine.  
3. Uploaded files will be saved into the selected directory.
""")

# 1️⃣ Choose target directory
target = st.selectbox(
    "Select target folder:",
    ("root", "data", "scripts")
)

# Map logical name → actual path
BASE_PATHS = {
    "root": ".",
    "data": "data",
    "scripts": "scripts"
}

# 2️⃣ File uploader (multiple)
uploaded_files = st.file_uploader(
    "Upload file(s):",
    type=None,
    accept_multiple_files=True
)

if uploaded_files:
    save_dir = BASE_PATHS[target]
    os.makedirs(save_dir, exist_ok=True)

    for uploaded in uploaded_files:
        dest_path = os.path.join(save_dir, uploaded.name)
        # Write file contents
        with open(dest_path, "wb") as f:
            f.write(uploaded.read())
        st.success(f"Saved **{uploaded.name}** to **{save_dir}/**")

    st.info("✅ All files uploaded successfully!")
