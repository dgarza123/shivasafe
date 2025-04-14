import streamlit as st
import pandas as pd

st.set_page_config(page_title="Transaction Explorer", layout="wide")
st.title("🧾 Transaction Explorer")

if "yaml_data" not in st.session_state or not st.session_state.yaml_data:
    st.warning("No YAML files loaded. Please upload files via the Home page.")
    st.stop()

# Flatten all transactions from loaded YAML files
records = []
for file_data in st.session_state.yaml_data:
    filename = file_data.get("_uploaded_filename", "unknown")
    for tx in file_data.get("transactions", []):
        tx = tx.get("transaction", tx)
        records.append({
            "Source File": filename,
            "Grantor": tx.get("grantor"),
            "Grantee": tx.get("grantee"),
            "Beneficiary": tx.get("beneficiary"),
            "Advisor": tx.get("advisor"),
            "Trust": tx.get("trust"),
            "Escrow #": tx.get("escrow_number"),
            "Escrow Officer": tx.get("escrow_officer"),
            "Amount": tx.get("amount"),
            "Parcel": tx.get("parcel_id"),
            "DLNR Match": tx.get("dlnr_match"),
            "Date Closed": tx.get("date_closed"),
            "Religious Assignment": tx.get("religious_assignment"),
            "Overseas Transfer": tx.get("overseas_transfer"),
        })

if not records:
    st.info("No transactions found in the loaded YAML files.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(records)

# Sidebar Filters
st.sidebar.header("Filter Transactions")
selected_entity = st.sidebar.text_input("Search by name (Grantor/Grantee/Beneficiary/Advisor)")
min_amount = st.sidebar.number_input("Minimum amount ($)", min_value=0, value=200000)
hide_dlnr_matches = st.sidebar.checkbox("Hide DLNR-confirmed parcels", value=False)

def parse_amount(val):
    try:
        return float(str(val).replace("$", "").replace(",", ""))
    except:
        return 0

# Apply filters
filtered_df = df.copy()
if selected_entity:
    filtered_df = filtered_df[filtered_df.apply(lambda row: selected_entity.lower() in str(row.values).lower(), axis=1)]

filtered_df = filtered_df[filtered_df["Amount"].apply(parse_amount) >= min_amount]
if hide_dlnr_matches:
    filtered_df = filtered_df[filtered_df["DLNR Match"] != True]

# Display
st.markdown(f"### Showing {len(filtered_df)} filtered transactions")
st.dataframe(filtered_df, use_container_width=True)
