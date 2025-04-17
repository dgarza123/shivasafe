import yaml
import os

yaml_dir = 'path_to_extracted_files'  # Replace this with your actual path
for file in os.listdir(yaml_dir):
    if file.endswith(".yaml"):
        with open(os.path.join(yaml_dir, file), "r") as f:
            try:
                data = yaml.safe_load(f)
                assert "transactions" in data, f"transactions missing in {file}"
                assert isinstance(data["transactions"], list), f"transactions not a list in {file}"
                for txn in data["transactions"]:
                    required_fields = ["parcel_id", "grantor", "grantee", "date_signed"]
                    missing = [field for field in required_fields if field not in txn]
                    assert not missing, f"Missing {missing} in {file}"
                print(f"{file} ✅ OK")
            except Exception as e:
                print(f"{file} ❌ ERROR: {e}")
