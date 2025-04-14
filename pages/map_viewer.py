import streamlit as st
import pydeck as pdk
import os
import yaml

st.set_page_config(page_title="Transaction Map", layout="wide")
st.title("Offshore Transaction Map")

TMP_DIR = "tmp"
ORIGIN_COORDS = [21.3069, -157.8583]  # Honolulu

def get_philippines_coords():
    return [13.41, 122.56]

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
        dest = get_philippines_coords()
        label_parts = [
            tx.get("grantee", "—"),
            tx.get("amount", ""),
            tx.get("parcel_id", ""),
        ]
        if not tx.get("parcel_valid", True):
            label_parts.append("❌ Invalid Parcel")
        if tx.get("registry_key"):
            label_parts.append(f"Key: {tx['registry_key']}")
        lines.append({
            "from_lat": ORIGIN_COORDS[0],
            "from_lon": ORIGIN_COORDS[1],
            "to_lat": dest[0],
            "to_lon": dest[1],
            "label": " | ".join([str(p) for p in label_parts if p]),
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
    get_width=1.5,
    get_source_color=[0, 100, 255],
    get_target_color="color",
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(
    latitude=ORIGIN_COORDS[0],
    longitude=ORIGIN_COORDS[1],
    zoom=3.6,
    pitch=20
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{label}"}
))
