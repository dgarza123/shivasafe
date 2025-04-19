import os
import streamlit as st

def run():
    st.title("🔼 Admin: Upload Evidence YAML")

    # point this at wherever you keep your YAMLs
    EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "evidence")
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    existing = [
        f for f in os.listdir(EVIDENCE_DIR)
        if f.lower().endswith((".yaml", ".yml"))
    ]
    st.write("Existing YAMLs:", existing or "_(none)_")

    uploaded = st.file_uploader(
        "Select one or more YAML files to upload",
        type=["yaml", "yml"],
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
            st.success(f"✅ Uploaded {len(uploaded)} file(s).")
