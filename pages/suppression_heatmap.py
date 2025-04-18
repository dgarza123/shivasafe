import streamlit as st
import pandas as pd
import pydeck as pdk
import os

st.set_page_config(page_title="Suppression Heatmap", layout="wide")
st.title("🧭 TMK Suppression Heatmap")

st.markdown("""
This map shows parcels that disappeared from public land records between 2018 and 2025.

### 🔎 Color Legend:
- 🔴 **Suppressed After Use**
- 🟡 **Vanished After Use**
- 🟢 **Still Public**
- ⚫️ **Fabricated / Never Listed**
""")

CSV_PATH = "Hawaii_tmk_suppression_status.csv"

# Load suppression data
if not os.path.exists(CSV_PATH):
    st.error(f"❌ File not found: {CSV_PATH}")
    st.stop()

try:
    df = pd.read_csv(CSV_PATH)
except Exception as e:
    st.error(f"❌ Failed to read CSV: {e}")
    st.stop()

# Sanity check
if df.empty or "classification" not in df.columns:
    st.error("❌ No valid suppression data found in file.")
    st.stop()

# Color logic by classification
def classify_color(row):
    cls = str(row["classification"])
    if "Suppressed" in cls:
        return [255, 0, 0]       # Red
    elif "Vanished" in cls:
        return [255, 200, 0]     # Yellow
    elif "Still Public" in cls:
        return [0, 255, 0]       # Green
    elif "Fabricated" in cls:
        return [50, 50, 50]      # Black
    return [120, 120, 120]       # Gray fallback

df["color"] = df.apply(classify_color, axis=1)

# Filter rows with valid coordinates
df = df.dropna(subset=["Latitude", "Longitude"])
df = df[df["Latitude"].apply(lambda x: isinstance(x, (int, float)))]
df = df[df["Longitude"].apply(lambda x: isinstance(x, (int, float)))]

if df.empty:
    st.warning("⚠️ No parcels with valid coordinates.")
    st.stop()

st.markdown(f"📍 Showing **{len(df)}** parcels with known coordinates")

# Deck layer
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[Longitude, Latitude]',
    get_fill_color="color",
    get_radius=1000,  # Large dot size
    pickable=True
)

view_state = pdk.ViewState(
    latitude=21.3,
    longitude=-157.85,
    zoom=9.5,
    pitch=0,
    bearing=0
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/streets-v12",
    tooltip={
        "html": "<b>TMK:</b> {TMK}<br><b>Status:</b> {classification}<br><b>File:</b> {document}"
    }
))
