# -------------------- pages/map_viewer.py --------------------
import streamlit as st
import os
import pandas as pd
import sqlite3
import pydeck as pdk

st.set_page_config(page_title="Parcel Map Viewer", layout="wide")
st.title("Parcel Transfer Map")

DB_PATH = "data/hawaii.db"
if not os.path.exists(DB_PATH):
    st.error("❌ hawaii.db missing in /data")
    st.stop()

try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM parcels", conn)
    conn.close()
except Exception as e:
    st.error(f"❌ Failed to load database: {e}")
    st.stop()

if df.empty:
    st.warning("No parcels found in database.")
    st.stop()

view = pdk.ViewState(latitude=20.8, longitude=-157.5, zoom=6.3, pitch=30)

arc_layer = pdk.Layer(
    "ArcLayer",
    data=df,
    get_source_position='[longitude, latitude]',
    get_target_position='[122.56, 11.6]',
    get_source_color='[255, 0, 0]',
    get_target_color='[255, 0, 0]',
    get_width=2,
    pickable=True,
)

tooltip = {
    "html": "<b>{certificate_id}</b><br />{parcel_id}<br />{grantee}<br />{amount}",
    "style": {"backgroundColor": "black", "color": "white"}
}

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=view,
    layers=[arc_layer],
    tooltip=tooltip
))
