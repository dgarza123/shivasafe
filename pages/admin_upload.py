import os
import streamlit as st
import yaml
import pandas as pd
import importlib.util
import sqlite3

EVIDENCE_DIR = "evidence"
DB_PATH = "data/hawaii.db"

st.set_page_config(page_title="Admin: Upload YAMLs + Rebuild", layout="centered")
st.title("📤 Upload YAML Evidence Files (No ZIP Required)")

# Optional cleanup button
if st.button("🧹 Clear all YAMLs in /evidence"):
    if os.path.exists(EVIDENCE_DIR):
        for root, _, files in os.walk(EVIDENCE_DIR):
            for file in files:
                if file.lower().endswith(".yaml"):
                    os.remove(os.path.join(root, file))
    st.success("✅ All YAMLs removed from /evidence")

# Upload field
uploaded_files = st.file_uploader("📄 Upload .yaml files (any name, 100 max)", type="yaml", accept_multiple_files=True)

saved_files = []
parse_issues = []

if uploaded_files:
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    for file in uploaded_files:
        try:
            raw_content = file.read().decode("utf-8")
            parsed = yaml.safe_load(raw_content)

            cert_num = parsed.get("certificate_number")
            if not cert_num:
                parse_issues.append({
                    "file": file.name,
                    "status": "❌ Skipped",
                    "reason": "Missing certificate_number"
                })
                continue

            new_filename = f"Certificate{cert_num}.yaml"
            dest_path = os.path.join(EVIDENCE_DIR, new_filename)

            with open(dest_path, "w", encoding="utf-8") as out:
                out.write(raw_content)

            saved_files.append(dest_path)

        except Exception as e:
            parse_issues.append({
                "file": file.name,
                "status": "❌ Error",
                "reason": str(e)
            })

    st.success(f"✅ Saved {len(saved_files)} file(s) to /evidence")

# Run validation on all .yaml files in evidence/
st.subheader("🔍 YAML Validation")

yaml_paths = []
for root, _, files in os.walk(EVIDENCE_DIR):
    for file in files:
        if file.lower().endswith(".yaml"):
            yaml_paths.append(os.path.join(root, file))

validation_results = []

required_top_fields = ["certificate_number", "document", "transactions"]
required_tx_fields = ["grantor", "grantee", "parcel_id"]

for path in yaml_paths:
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f)
        except Exception as e:
            validation_results.append({
                "file": os.path.relpath(path),
                "status": "❌ INVALID YAML",
                "problem": f"Parse error: {str(e)}"
            })
            continue

    for key in required_top_fields:
        if key not in data:
            validation_results.append({
                "file": os.path.relpath(path),
                "status": "⚠️ MISSING FIELD",
                "problem": f"Missing top-level field: {key}"
            })

    txs = data.get("transactions", [])
    if not isinstance(txs, list) or len(txs) == 0:
        validation_results.append({
            "file": os.path.relpath(path),
            "status": "⚠️ NO TRANSACTIONS",
            "problem": "transactions key is missing or empty"
        })
        continue

    for i, tx in enumerate(txs):
        for field in required_tx_fields:
            if field not in tx:
                validation_results.append({
                    "file": os.path.relpath(path),
                    "status": "⚠️ MISSING TX FIELD",
                    "problem": f"Missing '{field}' in transaction #{i + 1}"
                })

# Display results
if parse_issues:
    st.warning(f"⚠️ {len(parse_issues)} upload issues:")
    st.dataframe(pd.DataFrame(parse_issues))

if validation_results:
    st.warning(f"⚠️ {len(validation_results)} validation issue(s) found.")
    df = pd.DataFrame(validation_results)
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇️ Download Validation Report", df.to_csv(index=False), file_name="yaml_validation_issues.csv", mime="text/csv")
else:
    st.success("✅ All files passed validation.")

# Optional rebuild
if st.button("🔧 Rebuild hawaii.db from /evidence"):
    try:
        script_path = os.path.join("scripts", "rebuild_db_from_yaml.py")
        spec = importlib.util.spec_from_file_location("rebuild_db", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with st.spinner("Rebuilding database..."):
            count = module.build_db()

        st.success(f"✅ Rebuild complete: {count} transaction row(s) inserted.")

        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM parcels LIMIT 10", conn)
        conn.close()
        st.subheader("📄 Sample from Rebuilt Database:")
        st.dataframe(df)

    except Exception as e:
        st.error(f"❌ Rebuild failed: {e}")