# --- flagged.py ---
import streamlit as st
import yaml
import os
import pandas as pd

st.set_page_config(page_title="Flagged Entity Watchlist", layout="wide")
st.title("Flagged Entity Watchlist")

EVIDENCE_DIR = "evidence"
FLAGGED_NAMES = {
    "science of identity foundation",
    "chris butler",
    "jagad guru",
    "sif",
    "tulsi gabbard",
    "mike gabbard",
    "james campbell",
    "cameron nekota",
}

results = []

yaml_files = [f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml")]

for fname in yaml_files:
    try:
        with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict) or not isinstance(data.get("transactions"), list):
            continue
        for tx in data.get("transactions", []):
            if not isinstance(tx, dict):
                continue
            for field in ["grantor", "grantee", "beneficiary", "advisor", "trust"]:
                val = str(tx.get(field, "")).lower()
                for name in FLAGGED_NAMES:
                    if name in val:
                        results.append({
                            "Matched Name": name.title(),
                            "Role Field": field,
                            "Full Value": tx.get(field),
                            "Amount": tx.get("amount", ""),
                            "Parcel": tx.get("parcel_id", ""),
                            "Registry Key": tx.get("registry_key", ""),
                            "Offshore": tx.get("offshore_note", ""),
                            "File": fname,
                        })
    except Exception as e:
        st.warning(f"Error reading {fname}: {e}")

if not results:
    st.success("No flagged entities found.")
    st.stop()

df = pd.DataFrame(results)

st.subheader(f"Found {len(df)} flagged entries")
st.dataframe(df, use_container_width=True)

st.download_button("Download as CSV", df.to_csv(index=False), "flagged_entities.csv")