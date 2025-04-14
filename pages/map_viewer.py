# --- map_viewer.py ---
import streamlit as st
import pydeck as pdk
import os
import yaml

st.set_page_config(page_title="Transaction Map", layout="wide")
st.title("Offshore Transaction Map")

EVIDENCE_DIR = "evidence"

ORIGIN_LAT = 21.3069   # Honolulu
ORIGIN_LON = -157.8583
DEST_LAT = 13.41       # Philippines
DEST_LON = 122.56

arcs = []
markers = []

yaml_files = [f for f in os.listdir(EVIDENCE_DIR) if f.endswith("_entities.yaml")]

for fname in yaml_files:
    try:
        with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict) or not isinstance(data.get("transactions"), list):
            continue
        for tx in data["transactions"]:
            if not isinstance(tx, dict):
                continue
            if "offshore_note" not in tx:
                continue

            label = f"{tx.get('grantee', '')} | {tx.get('amount', '')} | {tx.get('parcel_id', '')}"
            if tx.get("registry_key"):
                label += f" | Key: {tx['registry_key']}"
            if not tx.get("parcel_valid", True):
                label += " (Invalid Parcel)"

            arcs.append({
                "from_lat": ORIGIN_LAT,
                "from_lon": ORIGIN_LON,
                "to_lat": DEST_LAT,
                "to_lon": DEST_LON,
                "label": label,
                "filename": fname,
                "color": [255, 0, 0],
            })

            markers.append({
                "lat": ORIGIN_LAT,
                "lon": ORIGIN_LON,
                "label": label,
                "filename": fname,
                "color": [0, 255, 0],
            })

    except Exception as e:
        st.warning(f"Could not read {fname}: {e}")

if not arcs:
    st.info("No offshore transactions found.")
    st.stop()

arc_layer = pdk.Layer(
    "ArcLayer",
    data=arcs,
    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],
    get_source_color="color",
    get_target_color="color",
    get_width=4,
    pickable=True,
    auto_highlight=True,
)

marker_layer = pdk.Layer(
    "ScatterplotLayer",
    data=markers,
    get_position=["lon", "lat"],
    get_color="color",
    get_radius=30000,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=ORIGIN_LAT,
    longitude=ORIGIN_LON,
    zoom=5,
    bearing=0,
    pitch=30,
)

st.pydeck_chart(pdk.Deck(
    layers=[arc_layer, marker_layer],
    initial_view_state=view_state,
    tooltip={"text": "{filename}\n{label}"}
))
