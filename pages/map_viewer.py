import streamlit as st
import pydeck as pdk
import pandas as pd

st.set_page_config(page_title="Minimal Map Test", layout="wide")
st.title("🧪 Minimal pydeck Test")

# 1 Point near Honolulu
df = pd.DataFrame({
    "lat": [21.3069],
    "lon": [-157.8583]
})

# Display data to confirm it's there
st.write("Loaded Test Data:")
st.dataframe(df)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius=150,
    get_fill_color=[255, 0, 0],
)

view_state = pdk.ViewState(
    latitude=21.3069,
    longitude=-157.8583,
    zoom=10,
)

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    layers=[layer],
    initial_view_state=view_state,
))
