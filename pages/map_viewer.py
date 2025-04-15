import streamlit as st
import pydeck as pdk
import os
import yaml
from hawaii_db import get_coordinates_by_tmk

st.set_page_config(page_title="Transaction Map", layout="wide")
st.title("Offshore Transaction Map")

EVIDENCE_DIR = "evidence"
DEFAULT_COORDS = [21.3069, -157.8583]  # Honolulu

def load_yaml_pairs():
    pairs = []
    for fname in os.listdir(EVIDENCE_DIR):
        if fname.endswith("_entities.yaml"):
            try:
                with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict) and "transactions" in data:
                    pairs.append((fname, data))
            except Exception as e:
                st.warning(f"Could not read {fname}: {e}")
    return pairs

def extract_lines(yaml_data, filename):
    lines = []
    for tx in yaml_data.get("transactions", []):
        if not isinstance(tx, dict):
            continue
        if "offshore_note" not in tx:
            continue

        tmk = str(tx.get("parcel_id", "")).strip()
        origin = get_coordinates_by_tmk(tmk) or DEFAULT_COORDS

        label = f"{tx.get('grantee', '')} | {tx.get('amount', '')} | {tmk}"
        if tx.get("registry_key"):
            label += f" | Key: {tx['registry_key']}"
        if not tx.get("parcel_valid", True):
            label += " (Invalid)"

        lines.append({
            "from_lat": origin[0],
            "from_lon": origin[1],
            "to_lat": 13.41,
            "to_lon": 122.56,
            "label": label,
            "filename": filename,
            "color": [255, 0, 0],
        })
    return lines

all_lines = []
for fname, ydata in load_yaml_pairs():
    all_lines.extend(extract_lines(ydata, fname))

if not all_lines:
    st.info("No offshore transactions found.")
    st.stop()

layer = pdk.Layer(
    "ArcLayer",
    data=all_lines,
    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],
    get_source_color="color",
    get_target_color="color",
    width_scale=0.0001,
    get_width=50,
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(
    latitude=DEFAULT_COORDS[0],
    longitude=DEFAULT_COORDS[1],
    zoom=2,
    bearing=0,
    pitch=30,
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{filename}\n{label}"}
))