import streamlit as st
import pydeck as pdk
import pandas as pd

st.set_page_config(page_title="Suppression Heatmap", layout="wide")
st.title("🔥 TMK Suppression Heatmap")

st.markdown("""
This map visualizes land parcels that were removed from public TMK datasets between 2018 and 2025.

- **Red** = Suppressed After Use  
- **Orange** = Inserted Then Vanished  
- **Purple** = Fabricated  
- **Blue** = Still Public  
""")

# Sample TMK suppression data
df = pd.DataFrame([
    {"TMK": "1-2-3:088", "Latitude": 21.356, "Longitude": -157.895, "classification": "Suppressed After Use"},
    {"TMK": "2-1-1:032", "Latitude": 21.402, "Longitude": -157.921, "classification": "Suppressed After Use"},
    {"TMK": "3-4-4:077", "Latitude": 19.738, "Longitude": -155.098, "classification": "Inserted Then Vanished"},
    {"TMK": "4-4-4:999", "Latitude": 21.000, "Longitude": -158.000, "classification": "Fabricated"},
    {"TMK": "1-3-2:114", "Latitude": 21.327, "Longitude": -157.861, "classification": "Still Public"},
])

# Assign color based on classification
def classify_color(status):
    if status == "Suppressed After Use":
        return [255, 0, 0]       # Red
    elif status == "Inserted Then Vanished":
        return [255, 165, 0]     # Orange
    elif status == "Fabricated":
        return [128, 0, 128]     # Purple
    else:
        return [0, 128, 255]     # Blue (Still Public)

df["color"] = df["classification"].apply(classify_color)

# Show the data for confirmation
st.subheader("📄 Loaded Suppression Records")
st.dataframe(df)

# Build the map layer
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
    zoom=7.2,
    pitch=0
)

# Show map
st.subheader("🗺️ Suppression Heatmap")
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "TMK: {TMK}\nStatus: {classification}"}
))
