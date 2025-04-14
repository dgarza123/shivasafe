import streamlit as st
from modules.hash_utils import compute_sha256_hash

st.set_page_config(page_title="Shiva Safe Upload", layout="wide")
st.title("Shiva PDF Upload – Chain-of-Custody Mode")
st.caption("Static-only upload. No preview. No decoding. No rendering. For SHA-256 fingerprint verification only.")

uploaded_file = st.file_uploader("Upload PDF (No Rendering Triggered)", type=["pdf"])

if uploaded_file:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
    sha256 = compute_sha256_hash(file_bytes)

    st.success("File uploaded without rendering.")
    st.markdown(f"**Filename:** `{filename}`")
    st.markdown(f"**SHA-256 Hash:** `{sha256}`")
    st.info("This hash can now be used for chain-of-custody logging or forensic correlation.")
