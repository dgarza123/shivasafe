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
                    assert "transactions" in data, "Missing 'transactions' key"
                    assert isinstance(data["transactions"], list), "'transactions' is not a list"
                    for txn in data["transactions"]:
                        required_fields = ["parcel_id", "grantor", "grantee", "date_signed"]
                        missing = [field for field in required_fields if field not in txn]
                        assert not missing, f"Missing fields: {missing}"
                    st.success(f"✅ {uploaded_file.name}: OK")
                except Exception as e:
                    st.error(f"❌ {uploaded_file.name}: {e}")
