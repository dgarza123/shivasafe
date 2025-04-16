import streamlit as st
import pandas as pd
import base64

st.set_page_config(page_title="Suppression Timeline", layout="wide")
st.title("📅 Parcel Suppression Timeline")

CSV_PATH = "tmk_suppression_timeline.csv"

@st.cache_data
def load_timeline_data():
    return pd.read_csv(CSV_PATH)

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")

def style_row(row):
    color = "#fff"
    if row["status"] == "Disappeared":
        color = "#ffe6e6"  # light red
    elif row["status"] == "Fabricated":
        color = "#f2f2f2"  # gray
    elif row["status"] == "Erased":
        color = "#fff0cc"  # light orange
    elif row["status"] == "Public":
        color = "#e6ffe6"  # light green
    return [f"background-color: {color}"] * len(row)

df = load_timeline_data()

# Convert bools to ✅/❌ if needed
for col in ["found_2018", "found_2022", "found_2025"]:
    df[col] = df[col].map({True: "✅", False: "❌", "Yes": "✅", "No": "❌"}).fillna("❌")

# Filters
st.sidebar.header("🔎 Filter Timeline")
status_filter = st.sidebar.multiselect("Suppression Status", df["status"].unique(), default=df["status"].unique())
df_filtered = df[df["status"].isin(status_filter)]

# Show styled table
st.dataframe(
    df_filtered.style.apply(style_row, axis=1),
    use_container_width=True,
    height=700
)

# Download CSV
csv_data = convert_df(df_filtered)
st.download_button(
    label="⬇️ Download Filtered Timeline CSV",
    data=csv_data,
    file_name="filtered_tmk_suppression_timeline.csv",
    mime="text/csv"
)