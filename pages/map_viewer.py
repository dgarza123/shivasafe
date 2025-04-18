import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk
import os

st.set_page_config(page_title="Parcel Suppression Map", layout="wide")
st.title("🗺️ TMK Suppression Viewer")

DB_PATH = "data/hawaii.db"
if not os.path.exists(DB_PATH):
    st.error("❌ hawaii.db not found.")
    st.stop()

try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM parcels", conn)
    conn.close()
except Exception as e:
    st.error(f"❌ Failed to load database: {e}")
    st.stop()

if df.empty:
    st.warning("No parcels available.")
    st.stop()

# Filter valid coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Define colors based on status
def status_color(status):
    if status == "Public":
        return [0, 200, 0]
    elif status == "Disappeared":
        return [255, 200, 0]
    elif status == "Fabricated":
        return [255, 0, 0]
    else:
        return [160, 160, 160]

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

# Tooltip with core info only
tooltip = {
    "html": """
        <b>{parcel_id}</b><br/>
        {status}<br/>
        <i>{grantor}</i> → <b>{grantee}</b>
    """,
    "style": {
        "backgroundColor": "black",
        "color": "white"
    }
}

# Center on Hawaii
view_state = pdk.ViewState(
    latitude=20.7967,
    longitude=-156.3319,
    zoom=7.2,
    pitch=30
)

# Render map
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/streets-v12",
    initial_view_state=view_state,
    layers=[scatter_layer],
    tooltip=tooltip
))
