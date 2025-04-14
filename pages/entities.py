import streamlit as st
from collections import defaultdict
import os
import yaml

st.set_page_config(page_title="Entity Intelligence", layout="wide")
st.title("Entity Intelligence Dashboard")

EVIDENCE_DIR = "evidence"
yaml_files = [f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml")]

if not yaml_files:
    st.warning("No YAML files found.")
    st.stop()

entity_roles = defaultdict(lambda: defaultdict(set))

for fname in yaml_files:
    path = os.path.join(EVIDENCE_DIR, fname)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for tx in data.get("transactions", []):
            for role in ["grantor", "grantee", "beneficiary", "advisor"]:
                name = tx.get(role)
                if name:
                    entity_roles[name]["roles"].add(role)
                    entity_roles[name]["files"].add(fname)
                    if tx.get("parcel_id"):
                        entity_roles[name]["parcels"].add(tx["parcel_id"])
                    if tx.get("amount"):
                        entity_roles[name]["amounts"].add(tx["amount"])
    except Exception as e:
        st.warning(f"Failed to read {fname}: {e}")

st.sidebar.header("Search Entity")
search_term = st.sidebar.text_input("Entity name contains")

filtered = {
    k: v for k, v in entity_roles.items()
    if not search_term or search_term.lower() in k.lower()
}

if not filtered:
    st.info("No matching entities found.")
    st.stop()

for name, data in sorted(filtered.items()):
    st.markdown(f"### {name}")
    st.markdown(f"- Roles: {', '.join(sorted(data['roles']))}")
    st.markdown(f"- Files: {', '.join(sorted(data['files']))}")
    if data["parcels"]:
        st.markdown(f"- Parcels: {', '.join(sorted(data['parcels']))}")
    if data["amounts"]:
        st.markdown(f"- Amounts: {', '.join(sorted(data['amounts']))}")
    st.markdown("---")
