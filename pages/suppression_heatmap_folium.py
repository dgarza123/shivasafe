import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="Suppression Heatmap (Folium)", layout="wide")
st.title("🧭 TMK Suppression Heatmap (2D Folium)")

CSV_PATH = "Hawaii_tmk_suppression_status.csv"

if not os.path.exists(CSV_PATH):
    st.error(f"❌ File not found: {CSV_PATH}")
    st.stop()

df = pd.read_csv(CSV_PATH)

if df.empty or "classification" not in df.columns:
    st.error("❌ CSV file does not contain expected 'classification' column.")
    st.stop()

# Drop rows with invalid coords
df = df.dropna(subset=["Latitude", "Longitude"])
df = df[df["Latitude"].apply(lambda x: isinstance(x, (float, int)))]
df = df[df["Longitude"].apply(lambda x: isinstance(x, (float, int)))]

if df.empty:
    st.warning("⚠️ No usable parcel coordinates found.")
    st.stop()

st.markdown(f"📍 Showing **{len(df)}** TMK parcels")

# Map base
m = folium.Map(location=[21.3049, -157.8577], zoom_start=11, tiles="CartoDB positron")

# Color logic
def get_color(cls):
    if "Suppressed" in cls:
        return "red"
    elif "Vanished" in cls:
        return "orange"
    elif "Still Public" in cls:
        return "green"
    elif "Fabricated" in cls:
        return "black"
    return "gray"

# Add markers
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=8,
        color=get_color(row["classification"]),
        fill=True,
        fill_color=get_color(row["classification"]),
        fill_opacity=0.8,
        popup=folium.Popup(f"<b>TMK:</b> {row['TMK']}<br><b>Status:</b> {row['classification']}", max_width=300)
    ).add_to(m)

# Render map
st_folium(m, width=1100, height=700)
