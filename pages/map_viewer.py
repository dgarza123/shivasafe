import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

def show(cur):
    st.title("Map Viewer")

    # Fetch parcel locations
    df = pd.read_sql(
        "SELECT parcel_id, latitude, longitude FROM parcels WHERE latitude IS NOT NULL AND longitude IS NOT NULL",
        cur.connection,
    ).astype({"latitude": float, "longitude": float})

    if df.empty:
        st.warning("No parcel data available.")
        return

    # Center map on Hawaii
    m = folium.Map(location=[21.3156, -157.8586], zoom_start=9)

    # Add markers
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=(row.latitude, row.longitude),
            radius=3,
            color="blue",
            fill=True,
            fill_opacity=0.6,
        ).add_to(m)

    # Render
    st_folium(m, width="100%", height=600)