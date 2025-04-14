import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="DLNR Parcel Checker", layout="wide")
st.title("🗺️ DLNR Parcel Match & Anomaly Detector")

if "yaml_data" not in st.session_state or not st.session_state.yaml_data:
    st.warning("No YAML files loaded. Please upload files via the Home page.")
    st.stop()

# Extract all parcel numbers
parcel_records = []
for file_data in st.session_state.yaml_data:
    filename = file_data.get("_uploaded_filename", "unknown")
    for tx in file_data.get("transactions", []):
        tx = tx.get("transaction", tx)
        parcel_id = tx.get("parcel_id")
        if parcel_id:
            parcel_records.append({
                "Parcel ID": parcel_id,
                "DLNR Match": tx.get("dlnr_match"),
                "Source File": filename,
                "Amount": tx.get("amount"),
                "Grantor": tx.get("grantor"),
                "Grantee": tx.get("grantee") or tx.get("beneficiary"),
                "Date": tx.get("date_closed"),
            })

if not parcel_records:
    st.info("No parcel IDs found in uploaded YAML files.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(parcel_records)

dlnr_missing = df[df["DLNR Match"] != True]
dlnr_confirmed = df[df["DLNR Match"] == True]

# Display Summary
st.subheader("❗ Parcels Without DLNR Match")
st.dataframe(dlnr_missing, use_container_width=True)

st.markdown("---")

st.subheader("✅ DLNR Confirmed Parcels")
st.dataframe(dlnr_confirmed, use_container_width=True)

# Export
st.download_button("📥 Download DLNR Anomaly List (CSV)", dlnr_missing.to_csv(index=False), "dlnr_anomalies.csv")
