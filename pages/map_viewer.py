# pages/map_viewer.py

import os
import streamlit as st
import sqlite3
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Parcel Map Viewer", layout="wide")
st.title("Parcel Transfer Map")

# Paths
DB_PATH = "data/hawaii.db"
CSV_PATH = "Hawaii.csv"

# 🔍 Check for required files
if not os.path.exists(DB_PATH):
    st.error("❌ Missing hawaii.db in /data")
    st.stop()

if not os.path.exists(CSV_PATH):
    st.error("❌ Missing Hawaii.csv in root directory")
    st.stop()

# 📥 Load database and coordinates
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM parcels WHERE status != 'Fabricated'", conn)
conn.close()

coord_df = pd.read_csv(CSV_PATH)
merged = pd.merge(df, coord_df, on="parcel_id", how="left")

if merged.empty:
    st.warning("No valid parcels to display.")
    st.stop()

# 🌍 Define view
view = pdk.ViewState(latitude=20.8, longitude=-157.5, zoom=6.3, pitch=30)

# 🎯 Status colors
status_colors = {
    "Public": [0, 200, 0],
    "Disappeared": [220, 0, 0],
    "Erased": [255, 165, 0],
}

# ➰ Create lines for transactions
lines = []
for _, row in merged.iterrows():
    lat = row.get("latitude")
    lon = row.get("longitude")
    if pd.isna(lat) or pd.isna(lon):
        continue

    color = [0, 0, 255] if row["status"] == "Public" else [255, 0, 0]
    lines.append({
        "from": [lon, lat],
        "to": [122.56, 11.6],  # Philippines
        "tooltip": f"{row['grantee']} — {row['amount']}",
        "color": color
    })

# 🔵 Map layers
scatter = pdk.Layer(
    "ScatterplotLayer",
    data=merged,
    get_position="[longitude, latitude]",
    get_fill_color="[200, 200, 200]",
    get_radius=250,
    pickable=True,
)

arc_layer = pdk.Layer(
    "ArcLayer",
    data=lines,
    get_source_position="from",
    get_target_position="to",
    get_width=2,
    get_source_color="color",
    get_target_color="color",
    pickable=True,
    auto_highlight=True,
)

tooltip = {
    "html": "<b>{certificate_id}</b><br />{parcel_id}<br />{grantee}<br />{amount}<br />{status}",
    "style": {"backgroundColor": "black", "color": "white"}
}

# 📍 Show map
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=view,
    layers=[scatter, arc_layer],
    tooltip=tooltip
))
