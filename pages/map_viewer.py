import streamlit as st
import pydeck as pdk
import os
import yaml
import re
import hashlib

st.set_page_config(page_title="Map Viewer", layout="wide")
st.title("Offshore Transaction Map")

TMP_DIR = "tmp"
ORIGIN_COORDS = [21.3069, -157.8583]  # Default: Honolulu, HI

def get_country_destination(note):
    if "philippines" in note.lower():
        return [13.41, 122.56]  # Central Philippines
    return [14.6, 121.0]  # Default fallback (Manila)

def load_yaml_pairs():
    pairs = []
    for fname in os.listdir(TMP_DIR):
        if fname.endswith("_entities.yaml"):
            base = fname.replace("_entities.yaml", "")
            pdf = base + ".pdf"
            if os.path.exists(os.path.join(TMP_DIR, pdf)):
                with open(os.path.join(TMP_DIR, fname), "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    pairs.append((pdf, data))
    return pairs

def extract_lines(yaml_data):
    lines = []
    for tx in yaml_data.get("transactions", []):
        if "offshore_note" not in tx:
            continue
        dest = get_country_destination(tx["offshore_note"])
        label = tx.get("grantee", "Unknown")
        parcel = tx.get("parcel_id", "—")
        amt = tx.get("amount", "—")
        reg = tx.get("registry_key", "")
        lines.append({
            "from_lat": ORIGIN_COORDS[0],
            "from_lon": ORIGIN_COORDS[1],
            "to_lat": dest[0],
            "to_lon": dest[1],
            "label": f"{label} | {amt} | {parcel} | {reg}",
            "direction": "outbound",
            "color": [255, 0, 0]  # Red for outbound
        })
    return lines

all_lines = []
for _, ydata in load_yaml_pairs():
    all_lines.extend(extract_lines(ydata))

if not all_lines:
    st.warning("No offshore transaction lines found.")
    st.stop()

layer = pdk.Layer(
    "ArcLayer",
    data=all_lines,
    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],
    get_width=2,
    get_source_color=[0, 100, 255],
    get_target_color="color",
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(latitude=ORIGIN_COORDS[0], longitude=ORIGIN_COORDS[1], zoom=3.5, pitch=0)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{label}"}
))
