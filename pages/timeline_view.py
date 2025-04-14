import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Transaction Timeline", layout="wide")
st.title("📆 Transaction Timeline Viewer")

if "yaml_data" not in st.session_state or not st.session_state.yaml_data:
    st.warning("No YAML files loaded. Please upload files via the Home page.")
    st.stop()

# Collect and flatten all transactions
records = []
for file_data in st.session_state.yaml_data:
    filename = file_data.get("_uploaded_filename", "unknown")
    for tx in file_data.get("transactions", []):
        tx = tx.get("transaction", tx)
        records.append({
            "Source File": filename,
            "Date Closed": tx.get("date_closed"),
            "From": tx.get("grantor"),
            "To": tx.get("grantee") or tx.get("beneficiary"),
            "Amount": tx.get("amount"),
            "Parcel": tx.get("parcel_id"),
            "Escrow #": tx.get("escrow_number"),
            "Trust": tx.get("trust"),
        })

# Convert to DataFrame
df = pd.DataFrame(records)
df = df.dropna(subset=["Date Closed"])  # Timeline needs date field
if df.empty:
    st.info("No transactions with valid dates available.")
    st.stop()

# Parse amounts and dates
def parse_amount(val):
    try:
        return float(str(val).replace("$", "").replace(",", ""))
    except:
        return 0

df["Amount"] = df["Amount"].apply(parse_amount)
df["Date Closed"] = pd.to_datetime(df["Date Closed"], errors='coerce')
df = df.dropna(subset=["Date Closed"])  # Drop rows with invalid date parsing

# Sort by date
df = df.sort_values("Date Closed")

# Render timeline chart
st.markdown("### 📊 Chronological Transfer Timeline")
fig = px.timeline(
    df,
    x_start="Date Closed",
    x_end="Date Closed",
    y="Trust",
    color="Amount",
    hover_data=["From", "To", "Escrow #", "Amount", "Parcel", "Source File"],
    title="Trust Transfers Over Time"
)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)
