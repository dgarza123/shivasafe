import streamlit as st
import hashlib
import os
import json
import yaml

st.set_page_config(layout="wide")
st.title("🧾 ShivaSafe — Upload & Review Forensic Results")

# === Upload Interface
uploaded_files = st.file_uploader("Upload forensic PDF containers", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    st.markdown("### 📄 Uploaded Files")

    for file in uploaded_files:
        file_bytes = file.read()
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        filename = file.name

        # Save to /tmp
        pdf_path = f"/tmp/{sha256}.pdf"
        with open(pdf_path, "wb") as f:
            f.write(file_bytes)

        # Display file summary
        st.markdown(f"- `{filename}` | SHA256: `{sha256[:12]}...` [📄 View PDF]({pdf_path})")

        # Auto-link YAML / JSON (if you've uploaded them separately)
        yaml_path = f"/tmp/{sha256}_entities.yaml"
        json_path = f"/tmp/{sha256}_blocks.json"

        if os.path.exists(yaml_path):
            st.markdown(f"⬇️ [Download YAML]({yaml_path})")

        if os.path.exists(json_path):
            st.markdown(f"⬇️ [Download JSON]({json_path})")

        st.markdown("---")

    # 🔄 Refresh page after upload
    st.success("✅ File(s) saved.")
    st.experimental_rerun()
