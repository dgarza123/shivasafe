import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Suppression Timeline", layout="wide")
st.title("📉 TMK Suppression Timeline")

st.markdown("""
This chart shows the number of land parcels that disappeared from the public TMK registry between major dataset snapshots:

- **2018–2022**: Moderate removals
- **2022–2025**: Aggressive suppression surge
""")

try:
    df = pd.read_csv("tmk_suppression_timeline.csv")
except Exception as e:
    st.error(f"Failed to load timeline CSV: {e}")
    st.stop()

# Plot bar chart
fig = px.bar(
    df,
    x="year_range",
    y="suppressed_tmk_count",
    text="suppressed_tmk_count",
    labels={"year_range": "Year Range", "suppressed_tmk_count": "TMKs Removed"},
    title="Number of TMKs Removed From Registry",
    color_discrete_sequence=["crimson"]
)

fig.update_traces(textposition='outside')
fig.update_layout(yaxis_title="Suppressed Parcels", xaxis_title="Year Range")

st.plotly_chart(fig, use_container_width=True)
