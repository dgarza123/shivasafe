import streamlit as st
import yaml
import os

st.set_page_config(layout="wide")
st.title("📂 Transaction Case Viewer")

# List available YAML reports
yamls = [f for f in os.listdir("/tmp") if f.endswith("_entities.yaml")]
if not yamls:
    st.warning("No case files found in /tmp.")
    st.stop()

selected = st.selectbox("Choose a report", yamls)

# Load selected YAML
path = os.path.join("/tmp", selected)
with open(path, "r", encoding="utf-8") as y:
    data = yaml.safe_load(y)

transactions = data.get("transactions", [])
st.markdown(f"### 📁 Showing {len(transactions)} extracted transaction(s) from `{selected}`")

for i, t in enumerate(transactions, 1):
    st.markdown(f"#### Transaction {i}")
    st.json(t)

# Offer matching PDF if it exists
base = selected.replace("_entities.yaml", "")
pdf_path = f"/tmp/{base}.pdf"
if os.path.exists(pdf_path):
    st.markdown(f"📄 [Download PDF]({pdf_path})")
