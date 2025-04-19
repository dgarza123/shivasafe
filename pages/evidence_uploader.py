# File: <your repo>/pages/evidence_uploader.py
import streamlit as st
from pathlib import Path

# 1) Locate (or create) the evidence/ folder at your repo root
EVIDENCE_DIR = Path(__file__).parent.parent / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="Evidence Uploader", layout="wide")
st.title("📁 Evidence Uploader")

st.markdown("""
Drop your transaction YAML files below (or click “Browse files”) —  
they’ll be saved into the `evidence/` folder.
""")

# 2) Let the user upload one or more YAML(.yaml|.yml) files
uploaded = st.file_uploader(
    "Select YAML files",
    type=["yaml", "yml"],
    accept_multiple_files=True
)

if uploaded:
    saved = []
    for up in uploaded:
        dest = EVIDENCE_DIR / up.name
        with open(dest, "wb") as f:
            f.write(up.getbuffer())
        saved.append(up.name)
    st.success(f"✔ Saved {len(saved)} file(s): " + ", ".join(saved))

st.markdown("---")

# 3) Show a live listing of what's in evidence/
st.subheader("Existing YAMLs in `evidence/`")
files = sorted(EVIDENCE_DIR.glob("*.y*ml"))
if not files:
    st.info("No YAML files found.")
else:
    for f in files:
        st.write("•", f.name)
