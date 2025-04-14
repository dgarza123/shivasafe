import streamlit as st
import yaml
import os
import datetime

st.set_page_config(page_title="Transaction Timeline", layout="wide")
st.title("Transaction Timeline")

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def load_transactions():
    entries = []
    for fname in os.listdir(EVIDENCE_DIR):
        if fname.endswith("_entities.yaml"):
            path = os.path.join(EVIDENCE_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                doc = data.get("document", fname)
                sha = data.get("sha256", "")[:12]
                for tx in data.get("transactions", []):
                    entries.append({
                        "date": tx.get("date_closed"),
                        "grantor": tx.get("grantor", "—"),
                        "grantee": tx.get("grantee", "—"),
                        "amount": tx.get("amount", "—"),
                        "parcel": tx.get("parcel_id", "—"),
                        "registry_key": tx.get("registry_key", ""),
                        "parcel_valid": tx.get("parcel_valid", True),
                        "doc": doc,
                        "sha": sha,
                    })
            except Exception as e:
                st.warning(f"Error loading {fname}: {e}")
    return sorted(entries, key=lambda x: x["date"] or "", reverse=True)

txs = load_transactions()

if not txs:
    st.info("No transaction data available.")
    st.stop()

for tx in txs:
    st.markdown("### ✅ Transaction" if tx["parcel_valid"] else "### 🟥 Transaction")
    st.markdown(f"- **From:** `{tx['grantor']}` → **To:** `{tx['grantee']}`")
    st.markdown(f"- **Amount:** `{tx['amount']}` | **Parcel:** `{tx['parcel']}`")
    if tx["registry_key"]:
        st.markdown(f"- **Registry Key:** `{tx['registry_key']}`")
    st.markdown(f"- **Document:** `{tx['doc']}` | SHA: `{tx['sha']}`")
    st.markdown("---")
