import streamlit as st
import os
import yaml
import io

st.set_page_config(page_title="Summary Report", layout="wide")
st.title("Summary Report Builder")

EVIDENCE_DIR = "evidence"
yaml_files = [f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml")]

if not yaml_files:
    st.warning("No YAML files available.")
    st.stop()

highlights = []

for fname in sorted(yaml_files):
    path = os.path.join(EVIDENCE_DIR, fname)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for tx in data.get("transactions", []):
            summary = []
            amount = tx.get("amount", "")
            parcel = tx.get("parcel_id", "")
            key = tx.get("registry_key", "")
            off = tx.get("offshore_note", "")
            valid = tx.get("parcel_valid", True)
            grtr = tx.get("grantor", "")
            grte = tx.get("grantee", "")
            if not grtr and not grte:
                continue
            if amount and isinstance(amount, str):
                try:
                    num = float(amount.replace("$", "").replace(",", ""))
                    if num < 200000:
                        continue
                except:
                    continue
            summary.append(f"{grtr} → {grte}")
            if amount:
                summary.append(f"Amount: {amount}")
            if parcel:
                summary.append(f"Parcel: {parcel}")
            if not valid:
                summary.append("Parcel: INVALID")
            if key:
                summary.append(f"Registry Key: {key}")
            if off:
                summary.append(f"Offshore: {off}")
            highlights.append(f"- {fname} | " + " | ".join(summary))
    except Exception as e:
        st.warning(f"Could not read {fname}: {e}")

if not highlights:
    st.info("No high-priority transactions found.")
    st.stop()

report_text = "\n".join(highlights)

st.subheader(f"Summary of {len(highlights)} flagged transactions")
st.text_area("Report Preview", report_text, height=500)

st.download_button(
    "Download Report (TXT)",
    data=report_text,
    file_name="summary_report.txt",
    mime="text/plain"
)
