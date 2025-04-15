import streamlit as st
import os
import yaml
from datetime import datetime

EVIDENCE_DIR = "evidence"
DEFAULT_COORDS = [21.3069, -157.8583]

st.set_page_config(page_title="Transaction Timeline", layout="wide")
st.title("📅 Forensic Transaction Timeline")

def load_yaml_pairs():
    pairs = []
    for fname in sorted(os.listdir(EVIDENCE_DIR)):
        if fname.endswith("_entities.yaml"):
            try:
                with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict) and "transactions" in data:
                    pairs.append((fname, data))
            except:
                continue
    return pairs

timeline = load_yaml_pairs()

if not timeline:
    st.info("No evidence files found.")
else:
    for fname, data in timeline:
        path = os.path.join(EVIDENCE_DIR, fname)
        mod_time = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"## {data.get('document', fname.replace('_entities.yaml', '.pdf'))}")
        st.caption(f"🕒 Last Modified: {mod_time}")
        st.caption(f"🔑 SHA256: `{data.get('sha256', 'unknown')}`")

        for tx in data.get("transactions", []):
            st.markdown("---")
            if "cert_id" in tx:
                st.markdown(f"#### Certificate: {tx['cert_id']}")

            for key, value in tx.items():
                if not value:
                    continue  # Skip empty values

                if key == "link":
                    st.markdown(f"- **Verification Link**: [{value}]({value})")
                elif isinstance(value, bool):
                    icon = "✅" if value else "❌"
                    st.markdown(f"- **{key.replace('_', ' ').title()}**: {icon}")
                else:
                    st.markdown(f"- **{key.replace('_', ' ').title()}**: {value}")

        st.markdown("---")