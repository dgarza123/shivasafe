import streamlit as st
import hashlib
import os
import yaml
import json
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")
st.title("🧾 ShivaSafe Forensic Transaction Dashboard")

# === 🔐 Admin Upload Access
admin_pass = st.sidebar.text_input("🔒 Admin Key", type="password")
is_admin = admin_pass == "shiva2024"  # <-- Change to your secure key

# === Admin Upload Interface (Visible only to you)
if is_admin:
    st.sidebar.markdown("### 📤 Upload Forensic Files")

    uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type=["pdf"], key="pdf")
    uploaded_yaml = st.sidebar.file_uploader("Upload YAML", type=["yaml", "yml"], key="yaml")

    if uploaded_pdf and uploaded_yaml:
        # Read and hash PDF
        file_bytes = uploaded_pdf.read()
        sha = hashlib.sha256(file_bytes).hexdigest()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_name = f"{timestamp}_{sha[:12]}"

        # Save files to /tmp
        pdf_path = f"/tmp/{base_name}.pdf"
        yaml_path = f"/tmp/{base_name}_entities.yaml"

        with open(pdf_path, "wb") as f:
            f.write(file_bytes)

        with open(yaml_path, "wb") as f:
            f.write(uploaded_yaml.getbuffer())

        st.sidebar.success(f"✅ Uploaded `{base_name}.pdf` and YAML")
        st.stop()  # Avoid rerun issues

# === 📂 Load YAML Transactions
def load_all_transactions():
    entries = []
    for f in os.listdir("/tmp"):
        if f.endswith("_entities.yaml"):
            try:
                with open(os.path.join("/tmp", f), "r", encoding="utf-8") as infile:
                    data = yaml.safe_load(infile)
                    for tx in data.get("transactions", []):
                        tx["_file"] = f
                        entries.append(tx)
            except:
                continue
    return entries

transactions = load_all_transactions()

if not transactions:
    st.warning("No transactions found.")
    st.stop()

# === 📊 Convert to DataFrame
def safe_date(d):
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
        "Registry Key": t.get("registry_key", ""),
        "Date": safe_date(t.get("date_closed")),
        "Source File": t.get("_file")
    }
    for t in transactions if t.get("amount")
])

# === 📋 Display + Sorting
st.markdown("### 📋 Latest Extracted Transactions")
sort_by = st.selectbox("Sort by", ["Date", "Amount", "Beneficiary"])
df = df.sort_values(sort_by, ascending=(sort_by != "Amount"))
st.dataframe(df, use_container_width=True)

# === 🔎 Detail View
selected = st.selectbox("Select a case file to view details", df["Source File"].unique())

with open(os.path.join("/tmp", selected), "r", encoding="utf-8") as f:
    case_data = yaml.safe_load(f)

st.markdown(f"### 📁 Transaction Details from `{selected}`")
for i, tx in enumerate(case_data.get("transactions", []), 1):
    st.markdown(f"#### Transaction {i}")
    st.json(tx)

# === 🔗 Navigation
st.markdown("---")
st.markdown("🗂 Use the sidebar to view:")
st.markdown("- 🌍 [Map Viewer](Map Viewer)")
st.markdown("- 📆 [Timeline](Timeline)")
st.markdown("- 📂 [Transaction Case Viewer](Transaction Case Viewer)")
