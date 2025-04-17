import os
import streamlit as st
import yaml
import pandas as pd

EVIDENCE_DIR = "evidence"

st.set_page_config(page_title="YAML Validator", layout="wide")
st.title("🔎 YAML Validator – Evidence Folder")

# Scan for YAML files
yaml_paths = []
for root, _, files in os.walk(EVIDENCE_DIR):
    for file in files:
        if file.lower().endswith(".yaml"):
            yaml_paths.append(os.path.join(root, file))

st.info(f"📁 Found {len(yaml_paths)} YAML file(s) in /evidence")

results = []

required_top_fields = ["certificate_number", "document", "transactions"]
required_tx_fields = ["grantor", "grantee", "parcel_id"]

for path in yaml_paths:
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            results.append({
                "file": os.path.relpath(path),
                "status": "❌ INVALID YAML",
                "problem": f"YAML parse error: {str(e)}"
            })
            continue

    # Top-level validation
    for key in required_top_fields:
        if key not in data:
            results.append({
                "file": os.path.relpath(path),
                "status": "⚠️ MISSING FIELD",
                "problem": f"Top-level key missing: {key}"
            })

    tx_list = data.get("transactions", [])
    if not isinstance(tx_list, list) or len(tx_list) == 0:
        results.append({
            "file": os.path.relpath(path),
            "status": "⚠️ NO TRANSACTIONS",
            "problem": "transactions key is missing, empty, or not a list"
        })
        continue

    # Per-transaction validation
    for i, tx in enumerate(tx_list):
        for f in required_tx_fields:
            if f not in tx:
                results.append({
                    "file": os.path.relpath(path),
                    "status": "⚠️ MISSING TX FIELD",
                    "problem": f"Missing '{f}' in transaction #{i + 1}"
                })

# Convert to DataFrame
df = pd.DataFrame(results)

if len(df) == 0:
    st.success("✅ All YAML files passed validation!")
else:
    st.warning(f"⚠️ {len(df)} issue(s) found:")
    st.dataframe(df, use_container_width=True)

    # CSV export
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download CSV Report", data=csv, file_name="yaml_validation_report.csv", mime="text/csv")
