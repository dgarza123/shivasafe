import streamlit as st
import hashlib
import os
import yaml
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")
st.title("ShivaSafe Forensic Transaction Dashboard")

# Admin Access
admin_pass = st.sidebar.text_input("Admin Key", type="password")
is_admin = admin_pass == "shiva2024"  # Change this as needed

# Admin: Upload Section
if is_admin:
    st.sidebar.markdown("### Upload Forensic Files")
    uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type=["pdf"], key="pdf")
    uploaded_yaml = st.sidebar.file_uploader("Upload YAML", type=["yaml", "yml"], key="yaml")

    if uploaded_pdf and uploaded_yaml:
        file_bytes = uploaded_pdf.read()
        sha = hashlib.sha256(file_bytes).hexdigest()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_name = f"{timestamp}_{sha[:12]}"
        pdf_path = f"/tmp/{base_name}.pdf"
        yaml_path = f"/tmp/{base_name}_entities.yaml"

        with open(pdf_path, "wb") as f:
            f.write(file_bytes)
        with open(yaml_path, "wb") as f:
            f.write(uploaded_yaml.getbuffer())

        st.sidebar.success(f"Uploaded as {base_name}")
        st.stop()

# Admin: Delete Section
if is_admin:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Delete Uploaded Files")
    tmp_files = sorted([f for f in os.listdir("/tmp") if f.endswith(".pdf") or f.endswith(".yaml")])
    file_to_delete = st.sidebar.selectbox("Select file", tmp_files)

    if st.sidebar.button("Delete Selected File"):
        try:
            os.remove(os.path.join("/tmp", file_to_delete))
            st.sidebar.success(f"Deleted: {file_to_delete}")
            st.stop()
        except Exception as e:
            st.sidebar.error(f"Failed to delete: {e}")

# Load YAML files
def load_transactions():
    records = []
    for f in os.listdir("/tmp"):
        if f.endswith("_entities.yaml"):
            with open(os.path.join("/tmp", f), "r", encoding="utf-8") as y:
                try:
                    data = yaml.safe_load(y)
                    for t in data.get("transactions", []):
                        t["_file"] = f
                        records.append(t)
                except:
                    continue
    return records

transactions = load_transactions()

if not transactions:
    st.warning("No YAML files in /tmp.")
    st.stop()

# Normalize to DataFrame
def parse_date(d):
    try:
        return datetime.strptime(str(d).strip(), "%Y-%m-%d")
    except:
        return None

df = pd.DataFrame([
    {
        "Beneficiary": t.get("beneficiary") or t.get("grantee"),
        "Grantor": t.get("grantor"),
        "Amount": t.get("amount"),
        "Parcel": t.get("parcel_id"),
        "Registry Key": t.get("registry_key"),
        "Date": parse_date(t.get("date_closed")),
        "Source File": t.get("_file")
    }
    for t in transactions if t.get("amount")
])

st.markdown("### Latest Transactions")
sort_by = st.selectbox("Sort by", ["Date", "Amount", "Beneficiary"])
df = df.sort_values(sort_by, ascending=(sort_by != "Amount"))
st.dataframe(df, use_container_width=True)

selected = st.selectbox("Select a YAML file", df["Source File"].unique())
with open(os.path.join("/tmp", selected), "r", encoding="utf-8") as f:
    st.markdown(f"### Details from {selected}")
    case = yaml.safe_load(f)
    for i, tx in enumerate(case.get("transactions", []), 1):
        st.markdown(f"#### Transaction {i}")
        st.json(tx)

st.markdown("---")
st.markdown("Use the sidebar to view:")
st.markdown("- Map Viewer")
st.markdown("- Timeline")
st.markdown("- Transaction Case Viewer")
