import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Suppression Heatmap", layout="wide")
st.title("🔥 TMK Suppression Heatmap")

st.markdown("""
This debug version renders a single hardcoded parcel to verify that the pydeck map engine is working.  
If you see a green dot over Honolulu, rendering is confirmed ✅.
""")

# === Static test data
df = pd.DataFrame([{
    "TMK": "TEST-PARCEL-123",
    "Latitude": 21.3069,
    "Longitude": -157.8583,
    "classification": "Debug Point",
    "color": [0, 255, 0]
}])

# Show the data to confirm it's loading
st.subheader("Loaded Data")
st.write("Row count:", df.shape[0])
st.dataframe(df)

# === Build test map layer
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[Longitude, Latitude]",
    get_fill_color="color",
    get_radius=100,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=21.3,
    longitude=-157.85,
    zoom=10,
    pitch=0
)

st.subheader("Rendered Map")
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "TMK: {TMK}\nStatus: {classification}"}
))
