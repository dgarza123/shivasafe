import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk
import os

st.set_page_config(page_title="Parcel Suppression Map", layout="wide")
st.title("🗺️ TMK Suppression Map")

DB_PATH = "data/hawaii.db"
if not os.path.exists(DB_PATH):
    st.error("❌ hawaii.db not found.")
    st.stop()

# Load data
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM parcels", conn)

    # Print DB schema
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(parcels);")
    schema_rows = cursor.fetchall()
    conn.close()

except Exception as e:
    st.error(f"❌ Failed to load DB: {e}")
    st.stop()

# Show actual schema
st.subheader("📋 Current DB Columns:")
st.code("\n".join([f"{col[1]} ({col[2]})" for col in schema_rows]))

# Check for required fields
required_fields = ["latitude", "longitude", "parcel_id", "grantor", "grantee", "status"]
missing = [col for col in required_fields if col not in df.columns]
if missing:
    st.error(f"❌ Your database is missing required column(s): {', '.join(missing)}")
    st.warning("Please delete `data/hawaii.db` and rebuild it using the correct `rebuild_db_from_yaml.py`.")
    st.stop()

# Filter valid coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Define color codes
def status_color(status):
    if status == "Public":
        return [0, 200, 0]
    elif status == "Disappeared":
        return [255, 200, 0]
    elif status == "Fabricated":
        return [255, 0, 0]
    return [160, 160, 160]

df["color"] = df["status"].apply(status_color)

# Build map
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[longitude, latitude]',
    get_radius=200,
    get_color="color",
    pickable=True,
)

tooltip = {
    "html": """
        <b>{parcel_id}</b><br/>
        {status}<br/>
        <i>{grantor}</i> → <b>{grantee}</b>
    """,
    "style": {"backgroundColor": "black", "color": "white"}
}

view_state = pdk.ViewState(
    latitude=20.7967,
    longitude=-156.3319,
    zoom=7.2,
    pitch=30
)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/streets-v12",
    initial_view_state=view_state,
    layers=[scatter_layer],
    tooltip=tooltip
))
