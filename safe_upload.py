import streamlit as st
from modules.hash_utils import compute_sha256_hash

st.set_page_config(page_title="Safe Upload", layout="wide")
st.title("Shiva Forensic Hash Verifier (Cloud Safe)")

uploaded_file = st.file_uploader("Upload PDF for hash check", type=["pdf"])

if uploaded_file:
    file_bytes = uploaded_file.getvalue()  # safer than .read()
    file_hash = compute_sha256_hash(file_bytes)

    st.success("✅ File received safely.")
    st.markdown(f"**SHA-256 Hash:** `{file_hash}`")
    st.info("File was never rendered or saved. Safe static hash only.")
