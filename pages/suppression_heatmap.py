import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
from folium.plugins import HeatMap

def show(cur):
    st.title("Suppression Status Heat Map")

    # Fetch only parcels with a numeric suppression score
    df = pd.read_sql(
        "SELECT latitude, longitude, suppression_status AS weight "
        "FROM parcels WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND suppression_status IS NOT NULL",
        cur.connection,
    ).astype({"latitude": float, "longitude": float, "weight": float})

    if df.empty:
        st.warning("No suppression data available.")
        return

    m = folium.Map(location=[21.3156, -157.8586], zoom_start=9)

    HeatMap(
        data=df[["latitude", "longitude", "weight"]].values.tolist(),
        radius=15,
        blur=10,
        max_zoom=12,
    ).add_to(m)

    st_folium(m, width="100%", height=600)
