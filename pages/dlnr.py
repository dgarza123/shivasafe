import streamlit as st
import os
import yaml
import pandas as pd

st.set_page_config(page_title="DLNR Checker", layout="wide")
st.title("🗺️ DLNR Parcel Anomaly Checker")

EVIDENCE_DIR = "evidence"
yaml_files = [f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml")]

parcels = []
for fname in yaml_files:
    try:
        with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for tx in data.get("transactions", []):
            parcels.append({
                "Parcel ID": tx.get("parcel_id"),
                "DLNR Match": tx.get("dlnr_match"),
                "Source File": fname,
                "Amount": tx.get("amount"),
                "Grantor": tx.get("grantor"),
                "Grantee": tx.get("grantee"),
                "Date": tx.get("date_closed"),
            })
    except Exception as e:
        st.warning(f"Could not load {fname}: {e}")

if not parcels:
    st.info("No parcel data found.")
    st.stop()

df = pd.DataFrame(parcels)
dlnr_missing = df[df["DLNR Match"] != True]
dlnr_confirmed = df[df["DLNR Match"] == True]

st.subheader("❗ Missing from DLNR")
st.dataframe(dlnr_missing, use_container_width=True)

st.markdown("---")

st.subheader("✅ DLNR Confirmed")
st.dataframe(dlnr_confirmed, use_container_width=True)

st.download_button("📥 Download DLNR Issues (CSV)", dlnr_missing.to_csv(index=False), "dlnr_issues.csv")
