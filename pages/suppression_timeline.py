import streamlit as st
import pandas as pd

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
    color = "#ffffff"
    if row["status"] == "Disappeared":
        color = "#ffe6e6"
    elif row["status"] == "Fabricated":
        color = "#f2f2f2"
    elif row["status"] == "Erased":
        color = "#fff0cc"
    elif row["status"] == "Public":
        color = "#e6ffe6"
    return [f"background-color: {color}"] * len(row)

# Load and normalize data
df = load_timeline_data()
df.columns = df.columns.str.strip().str.lower()

# Debug: show available columns
st.sidebar.caption("Detected CSV columns:")
st.sidebar.write(list(df.columns))

# Normalize year visibility columns to ✅ / ❌, even if missing
for col in ["found_2018", "found_2022", "found_2025"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().map({
            "True": "✅", "False": "❌", "Yes": "✅", "No": "❌", "✅": "✅", "❌": "❌"
        }).fillna("❌")
    else:
        df[col] = "❌"

# Sidebar filter for suppression status
if "status" in df.columns:
    status_filter = st.sidebar.multiselect("Suppression Status", df["status"].unique(), default=list(df["status"].unique()))
    df_filtered = df[df["status"].isin(status_filter)]
else:
    st.error("Missing 'status' column in the CSV.")
    df_filtered = df.copy()

# Display styled table
st.dataframe(
    df_filtered.style.apply(style_row, axis=1),
    use_container_width=True,
    height=700
)

# Download CSV export
csv_data = convert_df(df_filtered)
st.download_button(
    label="⬇️ Download Filtered Timeline CSV",
    data=csv_data,
    file_name="filtered_tmk_suppression_timeline.csv",
    mime="text/csv"
)