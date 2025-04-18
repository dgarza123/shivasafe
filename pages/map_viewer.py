import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk
import os

st.set_page_config(page_title="Parcel Map Viewer", layout="wide")
st.title("🗺️ Parcel Suppression Map")

DB_PATH = "data/hawaii.db"
if not os.path.exists(DB_PATH):
    st.error("❌ hawaii.db not found.")
    st.stop()

try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM parcels", conn)
    conn.close()
except Exception as e:
    st.error(f"❌ Failed to load DB: {e}")
    st.stop()

if df.empty:
    st.warning("No parcels found in database.")
    st.stop()

# Drop rows without coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Status-based color
def status_color(status):
    if status == "Public":
        return [0, 200, 0]        # Green
    elif status == "Disappeared":
        return [255, 200, 0]      # Yellow
    elif status == "Fabricated":
        return [255, 0, 0]        # Red
    else:
        return [160, 160, 160]    # Gray fallback

df["color"] = df["status"].apply(status_color)

# Map layer
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[longitude, latitude]',
    get_radius=200,
    get_color="color",
    pickable=True,
)

# Tooltip
tooltip = {
    "html": """
        <b>{certificate_id}</b><br/>
        {parcel_id}<br/>
        {status}<br/>
        <i>{grantor}</i> → <b>{grantee}</b><br/>
        {country}
    """,
    "style": {
        "backgroundColor": "black",
        "color": "white"
    }
}

# Hawaii-focused view
view_state = pdk.ViewState(
    latitude=20.7967,
    longitude=-156.3319,
    zoom=7.2,
    pitch=30
)

# Show map
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/streets-v12",
    initial_view_state=view_state,
    layers=[scatter_layer],
    tooltip=tooltip
))
