import streamlit as st
import yaml
import datetime
import io

st.set_page_config(page_title="Affidavit Report Builder", layout="wide")
st.title("📝 Forensic Affidavit Report Builder")

if "yaml_data" not in st.session_state or not st.session_state.yaml_data:
    st.warning("No YAML files loaded. Please upload files via the Home page.")
    st.stop()

st.sidebar.header("📂 Select Evidence Files")
file_names = [entry.get("_uploaded_filename") for entry in st.session_state.yaml_data]
selected_files = st.sidebar.multiselect("Include files in report:", options=file_names, default=file_names)

if not selected_files:
    st.info("Select at least one file to generate the report.")
    st.stop()

# Assemble report content
report = {
    "report_generated": datetime.datetime.utcnow().isoformat() + "Z",
    "included_files": [],
    "transactions": [],
    "flagged_entities": [],
    "pii_and_routing": [],
    "parcels_missing_dlnr": []
}

for entry in st.session_state.yaml_data:
    if entry.get("_uploaded_filename") not in selected_files:
        continue

    report["included_files"].append({
        "filename": entry.get("_uploaded_filename"),
        "sha256": entry.get("_sha256")
    })

    report["transactions"].extend(entry.get("transactions", []))
    report["flagged_entities"].extend(entry.get("flagged_entities", []))
    report["pii_and_routing"].extend(entry.get("pii_and_routing", []))

    for tx in entry.get("transactions", []):
        tx = tx.get("transaction", tx)
        if tx.get("dlnr_match") is not True:
            report["parcels_missing_dlnr"].append({
                "parcel_id": tx.get("parcel_id"),
                "source_file": entry.get("_uploaded_filename"),
                "grantor": tx.get("grantor"),
                "grantee": tx.get("grantee"),
                "amount": tx.get("amount"),
                "date": tx.get("date_closed")
            })

# YAML export
report_yaml = yaml.dump(report, sort_keys=False)
report_bytes = io.BytesIO(report_yaml.encode("utf-8"))

st.subheader("📄 Preview Report")
st.code(report_yaml, language="yaml")

st.download_button(
    label="📥 Download Full Report (YAML)",
    data=report_bytes,
    file_name="forensic_report.yaml",
    mime="application/x-yaml"
)
