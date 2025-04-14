import streamlit as st
import pandas as pd
import pydeck as pdk
import yaml
import os

st.set_page_config(layout="wide")
st.title("🌍 Global Transaction Map")

# === Load entity YAMLs from /tmp
def load_yaml_entities():
    entries = []
    for f in os.listdir("/tmp"):
        if f.endswith("_entities.yaml"):
            with open(os.path.join("/tmp", f), "r", encoding="utf-8") as infile:
                try:
                    data = yaml.safe_load(infile)
                    for t in data.get("transactions", []):
                        t["_source"] = f
                        entries.append(t)
                except:
                    continue
    return entries

entities = load_yaml_entities()
if not entities:
    st.warning("No entity YAML files found in /tmp.")
    st.stop()

# === Manual geolocation (fallback if no lat/lon exists)
LOCATION_LOOKUP = {
    "Kailua-Kona": (19.639994, -155.996926),
    "Waianae": (21.4379, -158.1859),
    "Honolulu": (21.3069, -157.8583),
}

def guess_location(row):
    addr = row.get("parcel_address", "")
    for city, coords in LOCATION_LOOKUP.items():
        if city.lower() in addr.lower():
            return coords
    return (21.3, -157.8)  # fallback (Hawaii default)

# === Build map data
points = []
for t in entities:
    lat, lon = t.get("lat"), t.get("lon")
    if not lat or not lon:
        lat, lon = guess_location(t)
    points.append({
        "lat": lat,
        "lon": lon,
        "amount": t.get("amount", ""),
        "name": t.get("beneficiary") or t.get("grantee") or "",
        "address": t.get("parcel_address", ""),
        "file": t.get("_source", "")
    })

df = pd.DataFrame(points)

# === Render Map
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(latitude=21.3, longitude=-157.8, zoom=7),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[lon, lat]',
            get_radius=3000,
            get_fill_color='[200, 30, 0, 160]',
            pickable=True
        )
    ],
    tooltip={"text": "{name}\n{amount}\n{address}\n{file}"}
))
