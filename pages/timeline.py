import streamlit as st
import os
import yaml
from datetime import datetime
from hawaii_db import get_coordinates_by_tmk

st.set_page_config(page_title="Transaction Timeline", layout="wide")
st.title("📅 Timeline of Extracted Transactions")

EVIDENCE_DIR = "evidence"
DEFAULT_COORDS = [21.3069, -157.8583]

# Load transactions from YAMLs
def load_transactions():
    timeline = []
    for fname in sorted(os.listdir(EVIDENCE_DIR)):
        if not fname.endswith("_entities.yaml"):
            continue
        path = os.path.join(EVIDENCE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict) or "transactions" not in data:
                continue
            for tx in data["transactions"]:
                if not isinstance(tx, dict):
                    continue
                sha = data.get("sha256", "unknown")
                tmk = tx.get("parcel_id", "").strip()
                coords = get_coordinates_by_tmk(tmk) or DEFAULT_COORDS
                timeline.append({
                    "file": data.get("document", fname.replace("_entities.yaml", ".pdf")),
                    "sha256": sha,
                    "grantor": tx.get("grantor", ""),
                    "grantee": tx.get("grantee", ""),
                    "amount": tx.get("amount", ""),
                    "parcel_id": tmk,
                    "coords": coords,
                    "registry_key": tx.get("registry_key", ""),
                    "offshore_note": tx.get("offshore_note", ""),
                    "valid": tx.get("parcel_valid", True),
                    "timestamp": datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d"),
                })
        except Exception as e:
            st.warning(f"Failed to load {fname}: {e}")
    return timeline

# Display timeline
timeline = load_transactions()
if not timeline:
    st.info("No transaction data found.")
    st.stop()

for tx in timeline:
    st.markdown(f"### {tx['file']} ({tx['timestamp']})")
    st.markdown(f"- **Grantor**: {tx['grantor']}")
    st.markdown(f"- **Grantee**: {tx['grantee']}")
    st.markdown(f"- **Amount**: {tx['amount']}")
    st.markdown(f"- **Parcel**: `{tx['parcel_id']}`")
    st.markdown(f"- **Valid Parcel**: {'✅' if tx['valid'] else '❌'}")
    st.markdown(f"- **Coordinates**: `{tx['coords'][0]:.5f}, {tx['coords'][1]:.5f}`")
    if tx["registry_key"]:
        st.markdown(f"- **Registry Key**: `{tx['registry_key']}`")
    if tx["offshore_note"]:
        st.markdown(f"- **Offshore Note**: _{tx['offshore_note']}_")
    st.markdown(f"- SHA256: `{tx['sha256']}`")
    st.markdown("---")
