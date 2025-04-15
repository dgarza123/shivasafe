import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Suppression Heatmap", layout="wide")
st.title("🔥 TMK Suppression Heatmap")

st.markdown("""
This map visualizes land parcels that were removed from public TMK datasets between 2018 and 2025.

- **Red points** = TMKs that appeared in 2018 or 2022, but were removed by 2025
- **Blue points** = TMKs still publicly listed in 2025
- Hover to view TMK and suppression status
""")

# Load suppression status CSV (must include: TMK, Latitude, Longitude, classification)
try:
    df = pd.read_csv("Hawaii_tmk_suppression_status.csv")
except FileNotFoundError:
    st.error("Suppression dataset not found. Make sure 'Hawaii_tmk_suppression_status.csv' is available.")
    st.stop()

# Assign colors by classification
def classify_color(status):
    if status == "Suppressed After Use":
        return [255, 0, 0]    # Red
    elif status == "Inserted Then Vanished":
        return [255, 165, 0]  # Orange
    elif status == "Fabricated":
        return [128, 0, 128]  # Purple
    else:
        return [0, 128, 255]  # Blue (Still Public)

df["color"] = df["classification"].apply(classify_color)

# Pydeck visualization
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[Longitude, Latitude]",
    get_fill_color="color",
    get_radius=60,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=21.3,
    longitude=-157.8,
    zoom=7.2,
    pitch=0
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "TMK: {TMK}\nStatus: {classification}"}
))