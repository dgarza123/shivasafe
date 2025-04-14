import streamlit as st
import yaml
import os
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")
st.title("📆 Transaction Timeline")

# === Load all YAMLs
def load_all_transactions():
    all_tx = []
    for f in os.listdir("/tmp"):
        if f.endswith("_entities.yaml"):
            with open(os.path.join("/tmp", f), "r", encoding="utf-8") as y:
                try:
                    data = yaml.safe_load(y)
                    for t in data.get("transactions", []):
                        t["_file"] = f
                        all_tx.append(t)
                except:
                    continue
    return all_tx

transactions = load_all_transactions()
if not transactions:
    st.warning("No transaction YAMLs found in /tmp.")
    st.stop()

# === Clean and sort by date
records = []
for tx in transactions:
    try:
        date = datetime.strptime(str(tx.get("date_closed", "")).strip(), "%Y-%m-%d")
    except:
        continue
    records.append({
        "date": date,
        "amount": tx.get("amount", ""),
        "beneficiary": tx.get("beneficiary") or tx.get("grantee"),
        "grantor": tx.get("grantor", ""),
        "parcel": tx.get("parcel_id", ""),
        "registry_key": tx.get("registry_key", ""),
        "source_file": tx.get("_file", "")
    })

df = pd.DataFrame(records).sort_values("date")

# === Display timeline
st.markdown("### 📋 Chronological View")
st.dataframe(df, use_container_width=True)
