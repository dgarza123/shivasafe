import os
import sqlite3
import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Parcel Map Viewer", layout="wide")
st.title("🗺️ Parcel Map Viewer")

DB_PATH = "data/hawaii.db"
if not os.path.exists(DB_PATH):
    st.error("❌ Database not found at data/hawaii.db. Please rebuild it first.")
    st.stop()

# 1) Load & filter
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM parcels", conn)
conn.close()

# Keep only valid numeric GPS
df = df.dropna(subset=["latitude", "longitude"])
df = df[
    df["latitude"].apply(lambda x: isinstance(x, (int, float))) &
    df["longitude"].apply(lambda x: isinstance(x, (int, float)))
]

if df.empty:
    st.warning("⚠️ No parcels with valid GPS found.")
    st.stop()

st.markdown(f"**Total parcels in DB:** {len(df)}    •  **Shown on map:** {len(df)}")

# 2) Status & DLNR flag
df["status"] = df["parcel_valid"].apply(lambda v: "Public" if v else "Disappeared")
df["is_dnrl"] = df["grantor"].str.contains("DLNR", case=False, na=False)

# 3) Color and radius
def pick_color(r):
    if r.is_dnrl:
        return [255, 0, 0]
    if r.status == "Disappeared":
        return [255, 200, 0]
    return [0, 200, 0]

df["color"] = df.apply(pick_color, axis=1)
df["radius"] = df["is_dnrl"].apply(lambda x: 300).astype(int)  # 300 m dots

# 4) PyDeck layer
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[longitude, latitude]',
    get_fill_color="color",
    get_radius="radius",
    pickable=True
)

tooltip = {
    "html": "<b>Parcel:</b> {parcel_id}<br/>"
            "<b>Grantor:</b> {grantor}<br/>"
            "<b>Grantee:</b> {grantee}<br/>"
            "<b>Amount:</b> {amount}<br/>"
            "<b>Status:</b> {status}",
    "style": {"backgroundColor":"black","color":"white"}
}

# Center on Oʻahu
view = pdk.ViewState(
    latitude=21.3050,
    longitude=-157.8577,
    zoom=11.2,
    pitch=0,
    bearing=0
)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v10",
    initial_view_state=view,
    layers=[layer],
    tooltip=tooltip
))
