# --- map_viewer.py (straight lines, parcel-centric) ---
import streamlit as st
import pydeck as pdk
import os
import yaml

st.set_page_config(page_title="Transaction Map", layout="wide")
st.title("Transaction Flow Map")

EVIDENCE_DIR = "evidence"

# Default: all parcels plotted at Honolulu
HAWAII_LAT = 21.3069
HAWAII_LON = -157.8583

def get_destination_coords(offshore_note):
    offshore_note = offshore_note.lower()
    if "philippines" in offshore_note:
        return (13.41, 122.56)
    if "dubai" in offshore_note:
        return (25.276987, 55.296249)
    if "japan" in offshore_note:
        return (35.6895, 139.6917)
    if "singapore" in offshore_note:
        return (1.3521, 103.8198)
    return (15.0, 120.0)  # generic fallback

lines = []
points = []

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
            offshore_note = tx.get("offshore_note", "")
            if not offshore_note:
                continue

            dest_lat, dest_lon = get_destination_coords(offshore_note)

            label = f"{tx.get('grantee', '')} | {tx.get('amount', '')} | {tx.get('parcel_id', '')}"
            if tx.get("registry_key"):
                label += f" | Key: {tx['registry_key']}"

            lines.append({
                "source_lon": HAWAII_LON,
                "source_lat": HAWAII_LAT,
                "target_lon": dest_lon,
                "target_lat": dest_lat,
                "label": label,
                "filename": fname,
            })

            points.append({
                "lon": HAWAII_LON,
                "lat": HAWAII_LAT,
                "label": label,
                "filename": fname,
            })

    except Exception as e:
        st.warning(f"Could not read {fname}: {e}")

if not lines:
    st.info("No offshore transactions found.")
    st.stop()

line_layer = pdk.Layer(
    "LineLayer",
    data=lines,
    get_source_position="[source_lon, source_lat]",
    get_target_position="[target_lon, target_lat]",
    get_width=3,
    get_color=[200, 0, 0],
    pickable=True
)

marker_layer = pdk.Layer(
    "ScatterplotLayer",
    data=points,
    get_position="[lon, lat]",
    get_color=[0, 180, 0],
    get_radius=30000,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=HAWAII_LAT,
    longitude=HAWAII_LON,
    zoom=5,
    pitch=30
)

st.pydeck_chart(pdk.Deck(
    layers=[marker_layer, line_layer],
    initial_view_state=view_state,
    tooltip={"text": "{filename}\n{label}"}
))
