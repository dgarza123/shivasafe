import streamlit as st
import yaml
import os

st.set_page_config(page_title="YAML Validator", layout="centered")
st.title("🔍 YAML File Validator")

# Let user select the directory containing YAML files
yaml_dir = st.text_input("Path to YAML directory", value="data/uploaded_yamls")

if yaml_dir:
    if not os.path.isdir(yaml_dir):
        st.error(f"❌ Directory does not exist: {yaml_dir}")
    else:
        yaml_files = [f for f in os.listdir(yaml_dir) if f.endswith(".yaml")]
        if not yaml_files:
            st.warning("⚠️ No YAML files found in the specified directory.")
        else:
            for file in yaml_files:
                path = os.path.join(yaml_dir, file)
                with open(path, "r") as f:
                    try:
                        data = yaml.safe_load(f)
                        assert "transactions" in data, "Missing 'transactions' key"
                        assert isinstance(data["transactions"], list), "'transactions' is not a list"
                        for txn in data["transactions"]:
                            required_fields = ["parcel_id", "grantor", "grantee", "date_signed"]
                            missing = [field for field in required_fields if field not in txn]
                            assert not missing, f"Missing fields: {missing}"
                        st.success(f"✅ {file}: OK")
                    except Exception as e:
                        st.error(f"❌ {file}: {e}")
