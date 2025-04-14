import streamlit as st
import yaml
import os
from datetime import datetime

st.set_page_config(page_title="📜 Transaction Timeline", layout="wide")
st.title("📜 Transaction Timeline")

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
                sha = data.get("sha256", "")[:12]
                doc = data.get("document", fname.replace("_entities.yaml", ".pdf"))
                mod_time = os.path.getmtime(path)
                for tx in data.get("transactions", []):
                    entries.append({
                        "grantor": tx.get("grantor", "—"),
                        "grantee": tx.get("grantee", "—"),
                        "amount": tx.get("amount", "$0"),
                        "parcel": tx.get("parcel_id", "—"),
                        "registry_key": tx.get("registry_key", ""),
                        "parcel_valid": tx.get("parcel_valid", True),
                        "offshore": tx.get("offshore_note", ""),
                        "sha": sha,
                        "doc": doc,
                        "mtime": mod_time,
                    })
            except Exception as e:
                st.warning(f"Could not read {fname}: {e}")
    return entries

entries = load_transactions()

if not entries:
    st.info("No transactions to display.")
    st.stop()

# Sort by amount descending
def parse_amount(a):
    try:
        return float(a["amount"].replace("$", "").replace(",", ""))
    except:
        return 0.0

entries = sorted(entries, key=parse_amount, reverse=True)

for tx in entries:
    badge = "✅" if tx["parcel_valid"] else "❌"
    tags = []
    if tx["offshore"]:
        tags.append("🌐 Offshore")
    if not tx["parcel_valid"]:
        tags.append("❌ Invalid Parcel")
    tag_str = " | ".join(tags)

    st.markdown(f"### {badge} `{tx['doc']}`")
    st.markdown(f"**SHA-256:** `{tx['sha']}`")
    st.markdown(f"**Date:** `{datetime.fromtimestamp(tx['mtime']).strftime('%Y-%m-%d %H:%M:%S')}`")
    st.markdown(f"- **From:** `{tx['grantor']}` → **To:** `{tx['grantee']}`")
    st.markdown(f"- **Amount:** `{tx['amount']}`")
    st.markdown(f"- **Parcel:** `{tx['parcel']}`")
    st.markdown(f"- **Registry Key:** `{tx['registry_key']}`")
    if tag_str:
        st.caption(tag_str)
    st.markdown("---")
