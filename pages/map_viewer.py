import streamlit as st
import pandas as pd
import pydeck as pdk
import yaml
import os

st.set_page_config(layout="wide")
st.title("Transaction Map with Routing Flows")

CITY_LOOKUP = {
    "Kailua-Kona": (19.64, -155.99),
    "Waianae": (21.4379, -158.1859),
    "Honolulu": (21.3069, -157.8583),
    "Maui": (20.7984, -156.3319),
    "Hilo": (19.713, -155.08)
}

OFFSHORE_LOOKUP = {
    "Philippines": (13.41, 122.56),
    "BDO": (14.583, 121.000),
    "UnionBank": (14.5547, 121.0244),
    "Switzerland": (46.8182, 8.2275),
    "Singapore": (1.3521, 103.8198),
    "Cayman": (19.3133, -81.2546)
}

def load_entities():
    entries = []
    for f in os.listdir("/tmp"):
        if f.endswith("_entities.yaml"):
            with open(os.path.join("/tmp", f), "r", encoding="utf-8") as infile:
                try:
                    data = yaml.safe_load(infile)
                    for tx in data.get("transactions", []):
                        tx["_source"] = f
                        entries.append(tx)
                except:
                    continue
    return entries

transactions = load_entities()
if not transactions:
    st.warning("No data.")
    st.stop()

markers = []
routes = []

for tx in transactions:
    addr = tx.get("parcel_address", "")
    city = next((k for k in CITY_LOOKUP if k.lower() in addr.lower()), "Honolulu")
    lat1, lon1 = CITY_LOOKUP[city]

    valid = tx.get("parcel_valid", True)
    color = [0, 100, 200, 160] if valid else [255, 0, 0, 180]
    marker_label = "Registered Parcel" if valid else "Unregistered Parcel"

    note = (tx.get("offshore_note", "") + " " + tx.get("bank", "") + " " + tx.get("swift_code", "")).lower()
    target = next(((lat, lon, name) for name, (lat, lon) in OFFSHORE_LOOKUP.items() if name.lower() in note), None)

    markers.append({
        "lat": lat1,
        "lon": lon1,
        "beneficiary": tx.get("beneficiary") or tx.get("grantee", ""),
        "amount": tx.get("amount", ""),
        "address": addr,
        "parcel_status": marker_label,
        "color": color
    })

    if target:
        lat2, lon2, label = target

        # Determine direction
        if any(p in note for p in ["assigned from", "received from", "funded by"]):
            direction_color = [0, 100, 200]  # Incoming = Blue
        else:
            direction_color = [200, 30, 0]   # Outgoing = Red

        routes.append({
            "from_lat": lat1,
            "from_lon": lon1,
            "to_lat": lat2,
            "to_lon": lon2,
            "color": direction_color,
            "label": f"{tx.get('beneficiary', '')} transfer",
            "amount": tx.get("amount", "")
        })

df_markers = pd.DataFrame(markers)
df_routes = pd.DataFrame(routes)

layers = [
    pdk.Layer(
        "ScatterplotLayer",
        data=df_markers,
        get_position='[lon, lat]',
        get_radius=3000,
        get_fill_color="color",
        pickable=True
    )
]

if not df_routes.empty:
    layers.append(
        pdk.Layer(
            "LineLayer",
            data=df_routes,
            get_source_position='[from_lon, from_lat]',
            get_target_position='[to_lon, to_lat]',
            get_color="color",
            get_width=3,
            pickable=True
        )
    )

st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(latitude=20.9, longitude=-157.9, zoom=6),
    layers=layers,
    tooltip={"text": "{beneficiary}\n{amount}\n{parcel_status}"}
))

st.markdown("**Legend**")
st.markdown("- Blue circle = Registered Parcel")
st.markdown("- Red circle = Unregistered Parcel (not in public TMK database)")
st.markdown("- Red line = Outgoing transfer (Hawaii → offshore)")
st.markdown("- Blue line = Incoming transfer (offshore → Hawaii)")
