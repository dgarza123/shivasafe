import streamlit as st
import pydeck as pdk
import os
import yaml
import pandas as pd

st.set_page_config(page_title="Transaction Map", layout="wide")
st.title("Offshore Transaction Map")

EVIDENCE_DIR = "evidence"
CENTROIDS_CSV = "Hawaii.csv"  # Ensure this file exists (extracted from Hawaii.zip)
DEFAULT_COORDS = [21.3069, -157.8583]  # Fallback to Honolulu

# Load TMK → (lat, lon) map
tmk_lookup = {}
try:
    df = pd.read_csv(CENTROIDS_CSV)
    for _, row in df.iterrows():
        tmk = str(row["TMK"]).strip()
        lat = float(row["Latitude"])
        lon = float(row["Longitude"])
        if lat != 0 and lon != 0:
            tmk_lookup[tmk] = (lat, lon)
except Exception as e:
    st.error(f"Error loading centroid CSV: {e}")
    st.stop()

# Load YAMLs
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

# Build arc lines
def extract_lines(yaml_data, filename):
    lines = []
    for tx in yaml_data.get("transactions", []):
        if not isinstance(tx, dict):
            continue
        if "offshore_note" not in tx:
            continue

        tmk = str(tx.get("parcel_id", "")).strip()
        origin = tmk_lookup.get(tmk, DEFAULT_COORDS)
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

# Run
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
