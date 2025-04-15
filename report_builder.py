import streamlit as st
import os
import yaml
from datetime import datetime

EVIDENCE_DIR = "evidence"
st.set_page_config(page_title="Download Reports", layout="wide")
st.title("🧾 Evidence Report Viewer")

def load_yaml_files():
    files = []
    for fname in sorted(os.listdir(EVIDENCE_DIR)):
        if fname.endswith("_entities.yaml"):
            try:
                with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if "transactions" in data:
                    files.append((fname, data))
            except Exception as e:
                st.warning(f"Could not read {fname}: {e}")
    return files

yaml_files = load_yaml_files()

if not yaml_files:
    st.info("No YAML reports found in /evidence/")
else:
    for fname, data in yaml_files:
        st.markdown("----")
        st.header(f"📄 {data.get('document', fname.replace('_entities.yaml', '.pdf'))}")
        st.caption(f"SHA256: `{data.get('sha256', 'unknown')}`")
        mod_time = datetime.fromtimestamp(os.path.getmtime(os.path.join(EVIDENCE_DIR, fname))).strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Last Modified: {mod_time}")

        for i, tx in enumerate(data.get("transactions", []), 1):
            st.subheader(f"Transaction {i}")
            for key, value in tx.items():
                if not value:
                    continue

                if key == "link":
                    st.markdown(f"- **Verification Link**: [{value}]({value})")
                elif isinstance(value, bool):
                    icon = "✅" if value else "❌"
                    st.markdown(f"- **{key.replace('_', ' ').title()}**: {icon}")
                else:
                    st.markdown(f"- **{key.replace('_', ' ').title()}**: {value}")