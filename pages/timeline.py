import streamlit as st
import yaml
import os
import datetime

st.set_page_config(page_title="Transaction Timeline", layout="wide")
st.title("Transaction Timeline")

EVIDENCE_DIR = "evidence"

def load_all_transactions():
    entries = []
    for fname in os.listdir(EVIDENCE_DIR):
        if not fname.endswith("_entities.yaml"):
            continue
        path = os.path.join(EVIDENCE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            doc = data.get("document", "").strip()
            sha = data.get("sha256", "").strip()
            pdf_path = os.path.join(EVIDENCE_DIR, doc)
            pdf_exists = os.path.exists(pdf_path)

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
                    "parcel_valid": tx.get("parcel_valid", True),
                    "pdf": doc,
                    "sha": sha,
                    "pdf_exists": pdf_exists,
                })
        except Exception as e:
            st.warning(f"Error reading {fname}: {e}")
    return sorted(entries, key=lambda x: x["date_obj"] or datetime.datetime.min)

timeline = load_all_transactions()

if not timeline:
    st.info("No transactions found.")
    st.stop()

for tx in timeline:
    badge = "✅" if tx["pdf_exists"] else "🟥"

    st.markdown(f"### {badge} {tx['date'] or 'Transaction'}")

    st.markdown(f"- **From:** `{tx['grantor']}` → **To:** `{tx['grantee']}`")
    st.markdown(f"- **Amount:** `{tx['amount']}` | **Parcel:** `{tx['parcel']}` {'✅' if tx['parcel_valid'] else '❌'}")

    if tx["registry_key"]:
        st.markdown(f"- **Registry Key:** `{tx['registry_key']}`")

    st.markdown(f"- **PDF:** `{tx['pdf']}`")
    if tx["pdf_exists"]:
        st.markdown(f"- **SHA256:** `{tx['sha'][:16]}...`")
    else:
        st.markdown(f"- **Missing PDF file**")

    st.markdown("---")