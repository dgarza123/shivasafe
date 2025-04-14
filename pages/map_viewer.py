import streamlit as st
import pydeck as pdk
import os
import yaml

st.set_page_config(page_title="Transaction Map", layout="wide")
st.title("Offshore Transaction Map")

EVIDENCE_DIR = "evidence"
os.makedirs(EVIDENCE_DIR, exist_ok=True)

ORIGIN_COORDS = [21.3069, -157.8583]

def get_philippines_coords():
    return [13.41, 122.56]

def load_yaml_pairs():
    pairs = []
    for fname in os.listdir(EVIDENCE_DIR):
        if fname.endswith("_entities.yaml"):
            try:
                with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        pairs.append((fname, data))
            except Exception as e:
                st.warning(f"Failed to read {fname}: {e}")
    return pairs

def extract_lines(yaml_data):
    lines = []
    for tx in yaml_data.get("transactions", []):
        if "offshore_note" not in tx:
            continue
        label = f"{tx.get('grantee')} | {tx.get('amount')} | {tx.get('parcel_id')}"
        if tx.get("registry_key"):
            label += f" | Key: {tx['registry_key']}"
        if not tx.get("parcel_valid", True):
            label += " ❌"
        lines.append({
            "from_lat": ORIGIN_COORDS[0],
            "from_lon": ORIGIN_COORDS[1],
            "to_lat": 13.41,
            "to_lon": 122.56,
            "label": label,
            "color": [255, 0, 0],
        })
    return lines

all_lines = []
for _, ydata in load_yaml_pairs():
    all_lines.extend(extract_lines(ydata))

if not all_lines:
    st.info("No offshore transactions found.")
    st.stop()

layer = pdk.Layer(
    "Arc
