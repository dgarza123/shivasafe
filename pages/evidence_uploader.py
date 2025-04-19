import os
import streamlit as st

# where your YAMLs live
EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "evidence")

def run():
    st.title("🔼 Admin: Upload Evidence YAML")
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    # list out what’s already there
    existing = [f for f in os.listdir(EVIDENCE_DIR) if f.lower().endswith(".yaml")]
    st.write("Existing files:", existing or "_(none)_")

    # uploader widget
    uploaded = st.file_uploader(
        "Select one or more YAML files to upload",
        type=["yaml"],
        accept_multiple_files=True,
    )

    if st.button("Upload"):
        if not uploaded:
            st.warning("No file selected.")
        else:
            for up in uploaded:
                dest = os.path.join(EVIDENCE_DIR, up.name)
                with open(dest, "wb") as out:
                    out.write(up.getbuffer())
            st.success(f"Uploaded {len(uploaded)} file(s) to `{EVIDENCE_DIR}`.")
