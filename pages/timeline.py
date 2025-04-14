import streamlit as st
import yaml
import os

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
                for tx in data.get("transactions", []):
                    entries.append({
                        "grantor": tx.get("grantor", "—"),
                        "grantee": tx.get("grantee", "—"),
                        "amount": tx.get("amount", "—"),
                        "parcel": tx.get("parcel_id", "—"),
                        "registry_key": tx.get("registry_key", ""),
                        "parcel_valid": tx.get("parcel_valid", True),
                        "sha": data.get("sha256", "")[:12],
                        "doc": data.get("document", fname.replace("_entities.yaml", ".pdf")),
                    })
            except Exception as e:
                st.warning(f"Could not read {fname}: {e}")
    return entries

entries = load_transactions()

if not entries:
    st.info("No transactions to display.")
    st.stop()

for tx in entries:
    badge = "✅" if tx["parcel_valid"] else "🟥"
    st.markdown(f"### {badge} Transaction")
    st.markdown(f"- **From:** `{tx['grantor']}` → **To:** `{tx['grantee']}`")
    st.markdown(f"- **Amount:** `{tx['amount']}` | **Parcel:** `{
