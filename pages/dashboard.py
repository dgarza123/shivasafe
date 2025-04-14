# --- dashboard.py ---
import streamlit as st
import pandas as pd
import os
import yaml

st.set_page_config(page_title="Transaction Explorer", layout="wide")
st.title("Transaction Explorer")

EVIDENCE_DIR = "evidence"
yaml_files = [f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml")]

records = []
for fname in yaml_files:
    try:
        with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict) or not isinstance(data.get("transactions"), list):
            continue
        for tx in data.get("transactions", []):
            if not isinstance(tx, dict):
                continue
            records.append({
                "Source File": fname,
                "Grantor": tx.get("grantor"),
                "Grantee": tx.get("grantee"),
                "Beneficiary": tx.get("beneficiary"),
                "Advisor": tx.get("advisor"),
                "Amount": tx.get("amount"),
                "Parcel": tx.get("parcel_id"),
                "DLNR Match": tx.get("dlnr_match"),
                "Date Closed": tx.get("date_closed"),
                "Offshore Transfer": tx.get("offshore_note") or tx.get("overseas_transfer"),
            })
    except Exception as e:
        st.warning(f"Could not load {fname}: {e}")

if not records:
    st.info("No transactions found.")
    st.stop()

df = pd.DataFrame(records)

st.sidebar.header("Filter Transactions")
search_term = st.sidebar.text_input("Search name or parcel")
min_amount = st.sidebar.number_input("Minimum amount ($)", min_value=0, value=200000)
hide_confirmed = st.sidebar.checkbox("Hide DLNR-confirmed", value=False)

def parse_amount(val):
    try:
        return float(str(val).replace("$", "").replace(",", ""))
    except:
        return 0

filtered_df = df.copy()
if search_term:
    filtered_df = filtered_df[filtered_df.apply(lambda row: search_term.lower() in str(row.values).lower(), axis=1)]
filtered_df = filtered_df[filtered_df["Amount"].apply(parse_amount) >= min_amount]
if hide_confirmed:
    filtered_df = filtered_df[filtered_df["DLNR Match"] != True]

st.markdown(f"Showing {len(filtered_df)} results")
st.dataframe(filtered_df, use_container_width=True)