import streamlit as st
import yaml
import os
import tempfile

st.set_page_config(page_title="YAML Validator", layout="centered")
st.title("🔍 YAML File Validator")

uploaded_files = st.file_uploader("Upload YAML files", type="yaml", accept_multiple_files=True)

if uploaded_files:
    with tempfile.TemporaryDirectory() as tmpdir:
        for uploaded_file in uploaded_files:
            path = os.path.join(tmpdir, uploaded_file.name)
            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with open(path, "r") as f:
                try:
                    data = yaml.safe_load(f)
                    assert isinstance(data, dict), "YAML root must be a dictionary"
                    required_top_level_fields = ["certificate_number", "sha256", "document", "transactions"]
                    missing_top_level = [field for field in required_top_level_fields if field not in data]
                    assert not missing_top_level, f"Missing top-level fields: {missing_top_level}"
                    assert isinstance(data["transactions"], list), "'transactions' must be a list"

                    for txn in data["transactions"]:
                        required_fields = [
                            "grantor", "grantee", "amount", "parcel_id", "parcel_valid",
                            "registry_key", "escrow_id", "transfer_bank", "country",
                            "routing_code", "account_fragment", "link", "gps",
                            "method", "signing_date"
                        ]
                        missing_fields = [field for field in required_fields if field not in txn]
                        assert not missing_fields, f"Missing transaction fields: {missing_fields}"
                    
                    st.success(f"✅ {uploaded_file.name}: OK")
                except Exception as e:
                    st.error(f"❌ {uploaded_file.name}: {e}")
