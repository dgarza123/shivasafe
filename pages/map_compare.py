import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("🗺️ Suppression Map Viewer")

DB_PATH = "data/hawaii.db"

# --- Load Database ---
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM parcels WHERE status != 'Fabricated'", conn)
    conn.close()
except Exception as e:
    st.error(f"❌ Failed to load database from {DB_PATH}")
    st.exception(e)
    st.stop()

if df.empty:
    st.warning("No parcels to display.")
    st.stop()

# --- Normalize coordinates ---
df = df.dropna(subset=["latitude", "longitude"])
df["latitude"] = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)

# --- Assign color based on status ---
color_map = {
    "Public": [0, 102, 204],        # Blue
    "Disappeared": [255, 0, 0],     # Red
    "Erased": [128, 128, 128],      # Gray
}
df["color"] = df["status"].map(color_map)

# --- Display map ---
st.subheader("Parcel Visibility Status (2018–2025)")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[longitude, latitude]',
    get_fill_color="color",
    get_radius=250,
    pickable=True,
)

tooltip = {
    "html": "<b>Parcel:</b> {parcel_id}<br>"
            "<b>Status:</b> {status}<br>"
            "<b>Cert:</b> {certificate_id}<br>"
            "<b>Grantee:</b> {grantee}<br>"
            "<b>Amount:</b> {amount}",
    "style": {"backgroundColor": "steelblue", "color": "white"}
}

view_state = pdk.ViewState(
    latitude=20.8,
    longitude=-156.3,
    zoom=6.2,
    pitch=0,
)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=view_state,
    layers=[layer],
    tooltip=tooltip
))
