# pages/upload_to_root.py

import os
import streamlit as st

# Compute your project root (two levels up from this file)
PAGE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(PAGE_DIR, os.pardir))

st.title("📤 Upload Files to Project Root")
st.markdown(
    """
    Use this page to upload any files (YAML, CSV, ZIP, etc.) and have them
    dropped into the **root** of your Streamlit app.  
    Typically your root is where `app.py`, `database_builder.py`, and `/data/` live.
    """
)

uploaded_files = st.file_uploader(
    "Pick one or more files to upload",
    type=None,
    accept_multiple_files=True,
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        dest_path = os.path.join(ROOT_DIR, uploaded_file.name)
        # avoid overwriting unless you really want to
        if os.path.exists(dest_path):
            if not st.confirm(f"`{uploaded_file.name}` already exists—overwrite?"):
                st.info(f"Skipped `{uploaded_file.name}`.")
                continue

        # write it out
        with open(dest_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✔️ Saved `{uploaded_file.name}` to `{dest_path}`")

    st.info("Once uploaded, switch back to your main page to rebuild your DB or re-run your scripts.")
