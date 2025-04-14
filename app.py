import streamlit as st
import os
import yaml
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("🧾 ShivaSafe Forensic Transaction Dashboard")

# === Load all YAMLs from /tmp/
def load_all_transactions():
    records = []
    for f in os.listdir("/tmp"):
        if f.endswith("_entities.yaml"):
            try:
                with open(os.path.join("/tmp", f), "r", encoding="utf-8") as y:
                    data = yaml.safe_load(y)
                    for tx in data.get("transactions", []):
                        tx["_file"] = f
                        records.append(tx)
            except:
                continue
    return records

transactions = load_all_transactions()

if not transactions:
    st.warning("No transactions found in `/tmp/`.")
    st.stop()

# === Flatten into DataFrame
def safe_date(d):
    try:
        return datetime.strptime(str(d).strip(), "%Y-%m-%d")
    except:
        return None

df = pd.DataFrame([
    {
        "Beneficiary": t.get("beneficiary") or t.get("grantee"),
        "Grantor": t.get("grantor"),
        "Amount": t.get("amount"),
        "Parcel": t.get("parcel_id"),
        "Registry Key": t.get("registry_key", ""),
        "Date": safe_date(t.get("date_closed")),
        "Source": t.get("_file")
    }
    for t in transactions if t.get("amount")
])

# === Sort + Filter Controls
st.markdown("### 📋 Recent Transactions")
sort_by = st.selectbox("Sort by", ["Date", "Amount", "Beneficiary"])
df = df.sort_values(sort_by, ascending=(sort_by != "Amount"))

# === Display Table
st.dataframe(df, use_container_width=True)

# === Detail Viewer
selected = st.selectbox("Select a record to view details", df["Source"].unique())

with open(os.path.join("/tmp", selected), "r", encoding="utf-8") as f:
    case_data = yaml.safe_load(f)

st.markdown(f"### 📁 Transaction Details from `{selected}`")
for i, tx in enumerate(case_data.get("transactions", []), 1):
    st.markdown(f"#### Transaction {i}")
    st.json(tx)

# === Navigation Help
st.markdown("---")
st.markdown("🔍 Use the sidebar to view:")
st.markdown("- 🌍 [Map Viewer](Map Viewer)")
st.markdown("- 📆 [Timeline](Timeline)")
st.markdown("- 📂 [Transaction Viewer](Transaction Case Viewer)")
