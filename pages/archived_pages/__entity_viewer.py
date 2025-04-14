import streamlit as st
from collections import defaultdict

st.set_page_config(page_title="Entity Intelligence", layout="wide")
st.title("🧠 Entity Intelligence Dashboard")

if "yaml_data" not in st.session_state or not st.session_state.yaml_data:
    st.warning("No YAML files loaded. Please upload files via the Home page.")
    st.stop()

# Collect all entities from transactions
entity_roles = defaultdict(lambda: defaultdict(set))

for file_data in st.session_state.yaml_data:
    filename = file_data.get("_uploaded_filename", "unknown")
    for tx in file_data.get("transactions", []):
        tx = tx.get("transaction", tx)
        for role in ["grantor", "grantee", "beneficiary", "advisor"]:
            name = tx.get(role)
            if name:
                entity_roles[name]["roles"].add(role)
                entity_roles[name]["files"].add(filename)
                if tx.get("parcel_id"):
                    entity_roles[name]["parcels"].add(tx.get("parcel_id"))
                if tx.get("amount"):
                    entity_roles[name]["amounts"].add(tx.get("amount"))

# Display searchable entity list
st.sidebar.header("🔎 Search Entity")
search_term = st.sidebar.text_input("Entity name contains")

filtered_entities = {
    k: v for k, v in entity_roles.items()
    if not search_term or search_term.lower() in k.lower()
}

if not filtered_entities:
    st.info("No matching entities found.")
    st.stop()

for name, data in sorted(filtered_entities.items()):
    st.markdown(f"### 🔹 {name}")
    st.markdown(f"- **Roles**: {', '.join(sorted(data['roles']))}")
    st.markdown(f"- **Appears in Files**: {', '.join(sorted(data['files']))}")
    if data["parcels"]:
        st.markdown(f"- **Parcels Linked**: {', '.join(sorted(data['parcels']))}")
    if data["amounts"]:
        st.markdown(f"- **Amounts Involved**: {', '.join(sorted(data['amounts']))}")
    st.markdown("---")
