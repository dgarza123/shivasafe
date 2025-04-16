import streamlit as st
import os
import zipfile

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

st.set_page_config(page_title="Upload & Unzip YAML Bundle")
st.title("📦 Upload Zipped YAMLs to /evidence")

uploaded_file = st.file_uploader("Upload a .zip file containing YAMLs", type="zip")

if uploaded_file:
    zip_path = os.path.join("temp_upload.zip")
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(EVIDENCE_DIR)
        st.success(f"✅ Extracted files to /{EVIDENCE_DIR}/")
    except Exception as e:
        st.error(f"❌ Failed to unzip: {e}")
    finally:
        os.remove(zip_path)

    # Show uploaded files
    st.markdown("### Extracted Files:")
    for fname in os.listdir(EVIDENCE_DIR):
        if fname.endswith(".yaml"):
            st.markdown(f"- `{fname}`")
