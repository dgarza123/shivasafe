import os
import streamlit as st
import yaml
import pandas as pd
import importlib.util
import sqlite3

EVIDENCE_DIR = "evidence"
DB_PATH = "data/hawaii.db"

st.set_page_config(page_title="Evidence Upload Tool", layout="centered")
st.title("📤 Upload Certificate YAML Files")

# Cleanup toggle
if st.button("🧹 Clear /evidence folder"):
    if os.path.exists(EVIDENCE_DIR):
        for root, _, files in os.walk(EVIDENCE_DIR):
            for file in files:
                if file.lower().endswith(".yaml"):
                    os.remove(os.path.join(root, file))
    st.success("✅ Cleared all YAMLs from /evidence")

# Upload interface
uploaded_files = st.file_uploader("📄 Upload YAML files (any name, up to 100)", type="yaml", accept_multiple_files=True)

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

    st.success(f"✅ Uploaded {len(saved_files)} file(s) to /evidence")

# Show current evidence count
existing = [f for f in os.listdir(EVIDENCE_DIR) if f.lower().endswith(".yaml")]
st.info(f"📦 {len(existing)} total YAML files currently in /evidence")

# Validation
st.subheader("🔍 Field Validation")

required_tx_fields = ["parcel_id", "gps", "grantor", "grantee", "country"]
validation_results = []

for path in existing:
    full_path = os.path.join(EVIDENCE_DIR, path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        validation_results.append({"file": path, "status": "❌ YAML Error", "problem": str(e)})
        continue

    txs = data.get("transactions", [])
    if not isinstance(txs, list) or len(txs) == 0:
        validation_results.append({"file": path, "status": "⚠️ Invalid", "problem": "No transactions list"})
        continue

    for i, tx in enumerate(txs):
        for fkey in ["grantor", "grantee", "country", "parcel_id"]:
            if not tx.get(fkey):
                validation_results.append({
                    "file": path,
                    "status": "⚠️ Missing Field",
                    "problem": f"{fkey} missing in TX #{i + 1}"
                })
        gps = tx.get("gps", [])
        if not (isinstance(gps, list) and len(gps) >= 2):
            validation_results.append({
                "file": path,
                "status": "⚠️ Invalid GPS",
                "problem": f"gps missing or incomplete in TX #{i + 1}"
            })

# Show results
if validation_results:
    st.warning(f"⚠️ {len(validation_results)} issue(s) found.")
    vdf = pd.DataFrame(validation_results)
    st.dataframe(vdf)
    st.download_button("⬇️ Download Validation Report", vdf.to_csv(index=False), file_name="yaml_validation_report.csv", mime="text/csv")
else:
    st.success("✅ All YAMLs passed validation.")

# Rebuild button
if st.button("🔧 Rebuild hawaii.db from current /evidence"):
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
        st.subheader("📄 Preview of Rebuilt Database:")
        st.dataframe(df)

    except Exception as e:
        st.error(f"❌ Rebuild failed: {e}")
