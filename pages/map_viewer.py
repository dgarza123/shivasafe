import streamlit as st
import pydeck as pdk
import os
import yaml

st.set_page_config(page_title="Transaction Map", layout="wide")
st.title("Offshore Transaction Map")

EVIDENCE_DIR = "evidence"
ORIGIN_COORDS = [21.3069, -157.8583]  # Honolulu, HI

def get_philippines_coords():
    return [13.41, 122.56]

def load_yaml_pairs():
    pairs = []
    for fname in os.listdir(EVIDENCE_DIR):
        if fname.endswith(".yaml") and "_entities" in fname:
            pdf_name = fname.replace("_entities.yaml", ".pdf")
            yaml_path = os.path.join(EVIDENCE_DIR, fname)
            pdf_path = os.path.join(EVIDENCE_DIR, pdf_name)
            if os.path.exists(pdf_path):
                try:
                    with open(yaml_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data:
                            pairs.append((pdf_name, data))
                except Exception as e:
                    st.warning(f"Failed to load {fname}: {e}")
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
            "label": " | ".join(str(p) for p in label_parts if p),
            "direction": "outbound",
            "color": [255, 0, 0],
        })
    return lines

all_lines = []
for _, ydata in load_yaml_pairs():
    try:
        all_lines.extend(extract_lines(ydata))
    except Exception as e:
        st.warning(f"Failed to parse transaction: {e}")

if not all_lines:
    st.info("No offshore transactions found.")
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
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=ORIGIN_COORDS[0],
    longitude=ORIGIN_COORDS[1],
    zoom=3.6,
    pitch=20,
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{label}"}
))