# pages/map_viewer.py

import os
import sqlite3
import pandas as pd
import streamlit as st
import pydeck as pdk
import chardet

st.set_page_config(page_title="Parcel Map Viewer", layout="wide")
st.title("Parcel Transfer Map")

# --- Load Database ---
DB_PATH = "data/hawaii.db"
if not os.path.exists(DB_PATH):
    st.error("❌ Missing hawaii.db in /data")
    st.stop()

try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM parcels WHERE status != 'Fabricated'", conn)
    conn.close()
except Exception as e:
    st.error(f"❌ Failed to load database: {e}")
    st.stop()

if df.empty:
    st.warning("No parcels found in database.")
    st.stop()

# --- Load Hawaii.csv Safely ---
if not os.path.exists("Hawaii.csv"):
    st.error("❌ Missing Hawaii.csv in project root.")
    st.stop()

try:
    with open("Hawaii.csv", "rb") as f:
        raw = f.read()
        encoding = chardet.detect(raw)["encoding"]
    coord_df = pd.read_csv("Hawaii.csv", encoding=encoding, on_bad_lines="skip")
    coord_df["parcel_id"] = coord_df["parcel_id"].astype(str).str.strip()
    coord_df["latitude"] = pd.to_numeric(coord_df["latitude"], errors="coerce")
    coord_df["longitude"] = pd.to_numeric(coord_df["longitude"], errors="coerce")
    coord_df = coord_df.dropna(subset=["latitude", "longitude"])
except Exception as e:
    st.error(f"❌ Failed to load Hawaii.csv: {e}")
    st.stop()

# --- Merge Coordinates ---
df["parcel_id"] = df["parcel_id"].astype(str).str.strip()
merged = pd.merge(df, coord_df, on="parcel_id", how="left")

if merged["latitude"].isnull().all():
    st.warning("No valid GPS coordinates matched parcel IDs.")
    st.stop()

# --- Define Map View ---
view = pdk.ViewState(latitude=20.8, longitude=-157.5, zoom=6.3, pitch=30)

# --- Define Colors ---
status_colors = {
    "Public": [0, 200, 0],
    "Disappeared": [220, 0, 0],
    "Erased": [255, 165, 0]
}

# --- Draw Parcels + Arcs ---
points = []
arcs = []
for _, row in merged.iterrows():
    lat, lon = row.get("latitude"), row.get("longitude")
    if pd.isna(lat) or pd.isna(lon):
        continue
    points.append({
        "coordinates": [lon, lat],
        "color": status_colors.get(row["status"], [150, 150, 150]),
        "tooltip": f"{row['certificate_id']}<br>{row['grantee']}<br>{row['amount']}"
    })
    if row.get("country", "").lower() == "philippines":
        arcs.append({
            "from": [lon, lat],
            "to": [122.56, 11.6],
            "color": [255, 0, 0]
        })
    elif row.get("country"):
        arcs.append({
            "from": [lon, lat],
            "to": [0, 0],  # fallback
            "color": [0, 0, 255]
        })

# --- Pydeck Layers ---
scatter = pdk.Layer(
    "ScatterplotLayer",
    data=points,
    get_position="coordinates",
    get_fill_color="color",
    get_radius=250,
    pickable=True,
)

arcs_layer = pdk.Layer(
    "ArcLayer",
    data=arcs,
    get_source_position="from",
    get_target_position="to",
    get_width=2,
    get_source_color="color",
    get_target_color="color",
    pickable=True,
    auto_highlight=True,
)

tooltip = {
    "html": "<b>{tooltip}</b>",
    "style": {"backgroundColor": "black", "color": "white"}
}

# --- Show Map ---
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=view,
    layers=[scatter, arcs_layer],
    tooltip=tooltip
))
