import streamlit as st
import os
import hashlib
import datetime
import yaml

st.set_page_config(page_title="ShivaSafe Evidence Admin", layout="wide")
st.title("ShivaSafe Admin Panel")

TMP_DIR = "tmp"
ADMIN_PASSWORD = "shiva2024"

# Auth
if "auth" not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    password = st.text_input("Enter admin password:", type="password")
    if password == ADMIN_PASSWORD:
        st.session_state.auth = True
        st.experimental_rerun()
    else:
        st.stop()

# Upload form
with st.expander("📤 Upload New Forensic Evidence"):
    with st.form("upload_form", clear_on_submit=True):
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
        yaml_file = st.file_uploader("Upload YAML", type=["yaml", "yml"])
        submitted = st.form_submit_button("Submit")

        if submitted and pdf_file and yaml_file:
            pdf_bytes = pdf_file.read()
            hash_id = hashlib.sha256(pdf_bytes).hexdigest()[:12]
            date_stamp = datetime.datetime.now().strftime("%Y-%m-%d")
            base = f"{date_stamp}_{hash_id}"

            os.makedirs(TMP_DIR, exist_ok=True)
            with open(os.path.join(TMP_DIR, base + ".pdf"), "wb") as f:
                f.write(pdf_bytes)
            with open(os.path.join(TMP_DIR, base + "_entities.yaml"), "wb") as f:
                f.write(yaml_file.read())

            st.success(f"Uploaded as `{base}`")
            st.experimental_rerun()

# File manager
st.subheader("🗂️ Current Evidence Files")

files = os.listdir(TMP_DIR)
pairs = sorted([f for f in files if f.endswith("_entities.yaml")])

if not pairs:
    st.info("No uploaded cases found.")
    st.stop()

for yname in pairs:
    base = yname.replace("_entities.yaml", "")
    ypath = os.path.join(TMP_DIR, yname)
    ppath = os.path.join(TMP_DIR, base + ".pdf")

    try:
        with open(ypath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        sha = data.get("sha256", "")[:12]
        doc = data.get("document", base)
        created = data.get("creation_date", "—")
        tx_count = len(data.get_
