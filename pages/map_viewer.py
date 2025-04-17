# pages/map_viewer.py

import os
import streamlit as st
import sqlite3
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Parcel Transfer Map", layout="wide")
st.title("Parcel Transfer Map")

# Load Hawaii.csv coordinates
CSV_PATH = "Hawaii.csv"
DB_PATH = "data/hawaii.db"

# Check for database
if not os.path.exists(DB_PATH):
    st.error("❌ Missing hawaii.db in /data")
    st.stop()

# Check for coordinate CSV
if not os.path.exists(CSV_PATH):
    st.error("❌ Missing Hawaii.csv in root folder.")
    st.stop()

# Load coordinates
coord_df = pd.read_csv(CSV_PATH)
coord_df.columns = [c.strip().lower() for c in coord_df.columns]

# Load transactions
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM parcels WHERE status != 'Fabricated'", conn)
conn.close()
df.columns = [c.strip().lower() for c in df.columns]

# Merge on parcel_id
if "parcel_id" not in df.columns or "parcel_id" not in coord_df.columns:
    st.error("❌ Missing 'parcel_id' column in data.")
    st.stop()

merged = pd.merge(df, coord_df, on="parcel_id", how="left")

if merged.empty:
    st.warning("No matching parcel data available.")
    st.stop()

# Define map view centered on Hawaii
view = pdk.ViewState(latitude=20.8, longitude=-157.5, zoom=6.3, pitch=30)

# Status color mapping
status_colors = {
    "public": [0, 200, 0],
    "disappeared": [220, 0, 0],
    "erased": [255, 165, 0]
}

# Points
scatter_data = []
arc_data = []

for _, row in merged.iterrows():
    lat = row.get("latitude")
    lon = row.get("longitude")
    status = str(row.get("status", "")).lower()

    if pd.isna(lat) or pd.isna(lon):
        continue

    # Add map point
    scatter_data.append({
        "position": [lon, lat],
        "status": status,
        "certificate": row.get("certificate_id", ""),
        "parcel": row.get("parcel_id", ""),
        "grantee": row.get("grantee", ""),
        "amount": row.get("amount", "")
    })

    # Offshore line if destination country
    if row.get("country"):
        to_coords = [122.56, 11.6]  # Philippines default
        if row["country"].lower() == "switzerland":
            to_coords = [8.54, 47.37]
        elif row["country"].lower() == "singapore":
            to_coords = [103.82, 1.35]

        arc_data.append({
            "from": [lon, lat],
            "to": to_coords,
            "color": [255, 0, 0] if status != "public" else [0, 0, 255],
            "tooltip": f"{row.get('grantee', '')} — {row.get('amount', '')}"
        })

# Deck layers
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=scatter_data,
    get_position="position",
    get_fill_color="color",
    get_radius=250,
    get_fill_color="[200, 200, 200]",
    pickable=True,
)

arc_layer = pdk.Layer(
    "ArcLayer",
    data=arc_data,
    get_source_position="from",
    get_target_position="to",
    get_source_color="color",
    get_target_color="color",
    get_width=2,
    pickable=True,
    auto_highlight=True,
)

tooltip = {
    "html": "<b>{certificate}</b><br />{parcel}<br />{grantee}<br />{amount}<br />{status}",
    "style": {"backgroundColor": "black", "color": "white"}
}

# Show map
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=view,
    layers=[scatter_layer, arc_layer],
    tooltip=tooltip
))
