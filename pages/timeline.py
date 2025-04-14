import streamlit as st
import yaml
import os
import datetime

st.set_page_config(page_title="Transaction Timeline", layout="wide")
st.title("Transaction Timeline")

TMP_DIR = "tmp"

def load_all_transactions():
    entries = []
    for fname in os.listdir(TMP_DIR):
        if not fname.endswith("_entities.yaml"):
            continue
        path = os.path.join(TMP_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            doc = data.get("document", fname)
            sha = data.get("sha256", "")[:12]
            for tx in data.get("transactions", []):
                date = tx.get("date_closed", None)
                try:
                    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d") if date else None
                except:
                    date_obj = None
                entries.append({
                    "date": date,
                    "date_obj": date_obj,
                    "grantor": tx.get("grantor", "—"),
                    "grantee": tx.get("grantee", "—"),
                    "amount": tx.get("amount", "—"),
                    "parcel": tx.get("parcel_id", "—"),
                    "registry_key": tx.get("registry_key", ""),
                    "status": tx.get("extraction_status", "unknown"),
                    "parcel_valid": tx.get("parcel_valid", True),
                    "doc": doc,
                    "sha": sha,
                })
        except Exception as e:
            st.warning(f"Error loading {fname}: {e}")
    return sorted(entries, key=lambda x: x["date_obj"] or datetime.datetime.min)

timeline = load_all_transactions()

if not timeline:
    st.info("No transactions found.")
    st.stop()

for tx in timeline:
    is_invalid = not tx["parcel_valid"]
    badge = "🟥" if is_invalid else "✅"

    # Display header
    if tx["date"]:
        st.markdown(f"### {badge} {tx['date']}")
    else:
        st.markdown(f"### {badge} Transaction")

    # Core details
    st.markdown(f"- **From:** `{tx['grantor']}` → **To:** `{tx['grantee']}`")
    st.markdown(f"- **Amount:** `{tx['amount']}` | **Parcel:** `{tx['parcel']}` {'❌' if is_invalid else '✅'}")

    if tx["registry_key"]:
        st.markdown(f"- **Registry Key:** `{tx['registry_key']}`")

    st.markdown(f"- **Source:** `{tx['doc']}` (SHA: `{tx['sha']}`)")
    st.markdown("---")
