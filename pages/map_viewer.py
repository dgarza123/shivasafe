import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk
import os

st.set_page_config(page_title="Parcel Suppression Map", layout="wide")
st.title("🗺️ Hawaii Parcel Suppression Map (2015–2025)")

# Load database
conn = sqlite3.connect("data/hawaii.db")
df = pd.read_sql_query("SELECT * FROM parcels", conn)
conn.close()

# Load coordinate map
coord_df = pd.read_csv("Hawaii.csv")  # must include parcel_id, lat, lon
coord_df.rename(columns={"TMK": "parcel_id"}, inplace=True)

# Join coordinates
merged = pd.merge(df, coord_df, on="parcel_id", how="left")
merged = merged.dropna(subset=["lat", "lon"])

# Suppression logic
def classify(row):
    if row["present_2015"] and row["present_2022"] and not row["present_2025"]:
        return "Disappeared"
    elif row["present_2015"] and not row["present_2022"] and not row["present_2025"]:
        return "Erased"
    elif not row["present_2015"] and row["present_2025"]:
        return "Fabricated"
    elif all([row["present_2015"], row["present_2018"], row["present_2022"], row["present_2025"]]):
        return "Public"
    return "Other"

merged["status"] = merged.apply(classify, axis=1)

# Color coding
color_map = {
    "Disappeared": [255, 0, 0],
    "Erased": [255, 165, 0],
    "Fabricated": [0, 100, 255],
    "Public": [0, 200, 0],
    "Other": [180, 180, 180],
}
merged["color"] = merged["status"].map(color_map)

# Layer
layer = pdk.Layer(
    "ScatterplotLayer",
    data=merged,
    get_position='[lon, lat]',
    get_fill_color="color",
    get_radius=60,
    pickable=True,
)

# Tooltip
tooltip = {
    "html": """
    <b>Parcel:</b> {parcel_id}<br/>
    <b>Status:</b> {status}<br/>
    <b>Certificate:</b> {certificate_id}<br/>
    <b>Grantee:</b> {grantee}<br/>
    <b>Amount:</b> {amount}<br/>
    """,
    "style": {"backgroundColor": "white", "color": "black"},
}

# Render
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=21.3,
        longitude=-157.8,
        zoom=7,
        pitch=0,
    ),
    layers=[layer],
    tooltip=tooltip,
))

# Summary table
with st.expander("📊 Suppression Breakdown"):
    st.dataframe(merged.groupby("status").size().reset_index(name="Count"))
