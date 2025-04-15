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

Data is loaded from `Hawaii_tmk_suppression_status.csv`
""")

# === Load data from file
try:
    df = pd.read_csv("Hawaii_tmk_suppression_status.csv")
    st.success(f"Loaded {len(df)} suppressed TMK records.")
except Exception as e:
    st.error(f"Error loading suppression file: {e}")
    st.stop()

# === Color logic
def classify_color(status):
    if status == "Suppressed After Use":
        return [255, 0, 0]
    elif status == "Inserted Then Vanished":
        return [255, 165, 0]
    elif status == "Fabricated":
        return [128, 0, 128]
    else:
        return [0, 128, 255]  # Still Public

df["color"] = df["classification"].apply(classify_color)

# === Preview the data
with st.expander("📄 Show TMK Table"):
    st.dataframe(df)

# === Build the map
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position="[Longitude, Latitude]",
    get_fill_color="color",
    get_radius=300,          # Larger for visibility
    get_line_color=[0, 0, 0],
    line_width_min_pixels=1,
    pickable=True,
    opacity=0.8
)

view_state = pdk.ViewState(
    latitude=21.3,
    longitude=-157.85,
    zoom=7.2,
    pitch=0
)

# === Show map
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "TMK: {TMK}\nStatus: {classification}"}
))
