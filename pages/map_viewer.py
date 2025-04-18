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

# ——————————————————————————————————————————————————————
# 1) Load & clean data
# ——————————————————————————————————————————————————————
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM parcels", conn)
conn.close()

# Drop anything without valid numeric GPS
df = (
    df
    .dropna(subset=["latitude", "longitude"])
    .loc[lambda d: d.latitude.apply(lambda x: isinstance(x, (int, float)))
                   & d.longitude.apply(lambda x: isinstance(x, (int, float)))]
)

if df.empty:
    st.warning("⚠️ No parcels with valid GPS found.")
    st.stop()

st.markdown(f"**Total parcels in DB:** {len(df)}    •  **Shown on map:** {len(df)}")

# ——————————————————————————————————————————————————————
# 2) Derive simple status & DLNR flag
# ——————————————————————————————————————————————————————
# If parcel_valid==True → Public, else Disappeared
df["status"] = df["parcel_valid"].apply(lambda v: "Public" if v else "Disappeared")

# Flag any grantor containing “DLNR”
df["is_dnrl"] = df["grantor"].str.contains("DLNR", case=False, na=False)

# ——————————————————————————————————————————————————————
# 3) Pick colors
# ——————————————————————————————————————————————————————
def pick_color(r):
    if r.is_dnrl:
        return [255, 0, 0]         # red for all DLNR sales
    if r.status == "Disappeared":
        return [255, 200, 0]       # amber for disappeared
    return [0, 200, 0]             # green for public

df["color"] = df.apply(pick_color, axis=1)

# ——————————————————————————————————————————————————————
# 4) Build PyDeck layer
# ——————————————————————————————————————————————————————
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[longitude, latitude]',
    get_fill_color="color",
    get_radius=800,
    pickable=True,
)

tooltip = {
    "html": "<b>Parcel:</b> {parcel_id}<br/>"
            "<b>Grantor:</b> {grantor}<br/>"
            "<b>Grantee:</b> {grantee}<br/>"
            "<b>Amount:</b> {amount}<br/>"
            "<b>Status:</b> {status}",
    "style": {"backgroundColor":"black","color":"white"}
}

# Center on O‘ahu
view = pdk.ViewState(
    latitude=21.3050,
    longitude=-157.8577,
    zoom=11.2,
    pitch=0,
    bearing=0
)

# ——————————————————————————————————————————————————————
# 5) Render map
# ——————————————————————————————————————————————————————
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v10",
    initial_view_state=view,
    layers=[layer],
    tooltip=tooltip
))
