import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk
import os
import importlib.util

st.set_page_config(page_title="Oʻahu Parcel Suppression Map", layout="wide")
st.title("🗺️ Suppression Map — Oʻahu Focused")

DB_PATH = "data/hawaii.db"
REBUILD_SCRIPT = "scripts/rebuild_db_from_yaml.py"

def load_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM parcels", conn)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(parcels);")
        schema = [col[1] for col in cursor.fetchall()]
        conn.close()
        return df, schema
    except Exception as e:
        st.error(f"❌ Failed to load DB: {e}")
        return None, []

def rebuild_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    spec = importlib.util.spec_from_file_location("rebuild_db", REBUILD_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inserted = module.build_db()
    st.info(f"🔁 Rebuilt hawaii.db with {inserted} rows")

# Load and verify
df, schema = load_database()
required_fields = ["latitude", "longitude", "parcel_id", "grantor", "grantee", "status"]
missing = [f for f in required_fields if f not in schema]

if missing:
    st.warning(f"⚠️ Missing columns: {', '.join(missing)} — rebuilding database...")
    rebuild_database()
    df, schema = load_database()

if df is None or df.empty:
    st.error("❌ No data available after rebuild.")
    st.stop()

# Drop invalid GPS
df = df.dropna(subset=["latitude", "longitude"])

# 💬 Debug preview
st.subheader("📋 Preview of Loaded Parcels")
st.write("✅ Rows with GPS:", len(df))
st.dataframe(df[["parcel_id", "latitude", "longitude", "grantor", "grantee", "status"]])

# Color logic
def status_color(status):
    if status == "Public":
        return [0, 200, 0]
    elif status == "Disappeared":
        return [255, 200, 0]
    elif status == "Fabricated":
        return [255, 0, 0]
    return [160, 160, 160]

df["color"] = df["status"].apply(status_color)

# Map layer
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[longitude, latitude]',
    get_radius=1200,
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

# 🔒 Locked view — Oʻahu, no pitch or bearing
view_state = pdk.ViewState(
    latitude=21.3049,
    longitude=-157.8577,
    zoom=11,
    pitch=0,
    bearing=0
)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/streets-v12",
    initial_view_state=view_state,
    layers=[scatter_layer],
    tooltip=tooltip
))
