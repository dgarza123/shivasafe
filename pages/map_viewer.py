import streamlit as st
import pandas as pd
import pydeck as pdk
import yaml
import os

st.set_page_config(layout="wide")
st.title("Global Transaction Map with Routing Flows")

# Hardcoded lookup for approximate parcel and offshore locations
CITY_LOOKUP = {
    "Kailua-Kona": (19.639994, -155.996926),
    "Waianae": (21.4379, -158.1859),
    "Honolulu": (21.3069, -157.8583),
    "Maui": (20.7984, -156.3319)
}

OFFSHORE_LOOKUP = {
    "Philippines": (13.41, 122.56),
    "BDO": (14.583, 121.000),  # Manila
    "UnionBank": (14.5547, 121.0244),  # Metro Manila
    "Switzerland": (46.8182, 8.2275),
    "Singapore": (1.3521, 103.8198),
    "Cayman": (19.3133, -81.2546)
}

# Load all transactions from /tmp
def load_yaml_entities():
    entries = []
    for f in os.listdir("/tmp"):
        if f.endswith("_entities.yaml"):
            try:
                with open(os.path.join("/tmp", f), "r", encoding="utf-8") as infile:
                    data = yaml.safe_load(infile)
                    for tx in data.get("transactions", []):
                        tx["_source"] = f
                        entries.append(tx)
            except:
                continue
    return entries

transactions = load_yaml_entities()
if not transactions:
    st.warning("No transactions found.")
    st.stop()

# Build data for map
markers = []
routes = []

for tx in transactions:
    addr = tx.get("parcel_address", "")
    city = None
    for k in CITY_LOOKUP:
        if k.lower() in addr.lower():
            city = k
            break
    if not city:
        city = "Honolulu"  # Default fallback

    source_lat, source_lon = CITY_LOOKUP[city]
    offshore_note = tx.get("offshore_note", "") + " " + tx.get("bank", "") + " " + tx.get("swift_code", "")
    offshore_target = None

    for name, (lat, lon) in OFFSHORE_LOOKUP.items():
        if name.lower() in offshore_note.lower():
            offshore_target = (lat, lon, name)
            break

    markers.append({
        "lat": source_lat,
        "lon": source_lon,
        "beneficiary": tx.get("beneficiary") or tx.get("grantee", ""),
        "amount": tx.get("amount", ""),
        "address": addr,
        "file": tx.get("_source")
    })

    if offshore_target:
        target_lat, target_lon, country = offshore_target
        routes.append({
            "from_lat": source_lat,
            "from_lon": source_lon,
            "to_lat": target_lat,
            "to_lon": target_lon,
            "label": f"{tx.get('beneficiary', '')} → {country}",
            "amount": tx.get("amount", "")
        })

# Create DataFrames
marker_df = pd.DataFrame(markers)
route_df = pd.DataFrame(routes)

# Define map layers
layers = [
    pdk.Layer(
        "ScatterplotLayer",
        data=marker_df,
        get_position='[lon, lat]',
        get_radius=3500,
        get_fill_color='[0, 100, 200, 160]',
        pickable=True,
    )
]

if not route_df.empty:
    layers.append(
        pdk.Layer(
            "LineLayer",
            data=route_df,
            get_source_position='[from_lon, from_lat]',
            get_target_position='[to_lon, to_lat]',
            get_width=3,
            get_color=[200, 30, 0],
            pickable=True
        )
    )

# Render map
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(latitude=21.3, longitude=-157.8, zoom=6),
    layers=layers,
    tooltip={"text": "{beneficiary}\n{amount}\n{address}"}
))
