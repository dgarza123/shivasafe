import streamlit as st
import pydeck as pdk
import pandas as pd

st.set_page_config(page_title="🧪 Minimal Map Test", layout="wide")
st.title("🧪 TMK Suppression Map Debug")

st.markdown("""
This is a minimal test to verify map rendering.  
You should see **one red dot** centered over Honolulu.  
If nothing appears, it's a rendering issue (not data).
""")

# Test DataFrame with 1 point
df = pd.DataFrame({
    "lat": [21.3069],        # Latitude of Honolulu
    "lon": [-157.8583]       # Longitude of Honolulu
})

st.subheader("📄 Test DataFrame:")
st.dataframe(df)

# Minimal Scatterplot Layer
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[lon, lat]',
    get_radius=150,
    get_fill_color=[255, 0, 0],
    pickable=False
)

# View Settings
view_state = pdk.ViewState(
    latitude=21.3069,
    longitude=-157.8583,
    zoom=10,
    pitch=0
)

# Display map
st.subheader("🗺️ Rendered Map:")
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    layers=[layer],
    initial_view_state=view_state
))
