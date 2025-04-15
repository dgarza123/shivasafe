import streamlit as st
import os
import yaml
import pydeck as pdk
from hawaii_db import get_coordinates_by_tmk

EVIDENCE_DIR = "evidence"
DEFAULT_COORDS = [21.3069, -157.8583]

st.set_page_config(page_title="Offshore Transaction Map", layout="wide")
st.title("🌐 Offshore Transaction Map")

def load_yaml_files():
    results = []
    for fname in os.listdir(EVIDENCE_DIR):
        if fname.endswith("_entities.yaml"):
            try:
                with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                results.append((fname, data))
            except:
                continue
    return results

def extract_arcs(yaml_data, filename):
    arcs = []
    for tx in yaml_data.get("transactions", []):
        if "country" not in tx:
            continue  # skip if no offshore data

        if tx["country"].lower() not in ["philippines", "singapore"]:
            continue  # show only offshore transfers

        tmk = str(tx.get("parcel_id", "")).replace("TMK", "").strip()
        coords = get_coordinates_by_tmk(tmk) or DEFAULT_COORDS

        label_parts = [
            f"Grantee: {tx.get('grantee', '')}",
            f"Amount: {tx.get('amount', '')}",
            f"Parcel: {tmk}",
        ]
        if tx.get("registry_key"):
            label_parts.append(f"Key: {tx['registry_key']}")
        if tx.get("link"):
            label_parts.append(f"URL: {tx['link']}")
        label = " | ".join(label_parts)

        arcs.append({
            "from_lat": coords[0],
            "from_lon": coords[1],
            "to_lat": 13.41 if tx["country"].lower() == "philippines" else 1.29,
            "to_lon": 122.56 if tx["country"].lower() == "philippines" else 103.85,
            "label": label,
            "filename": filename,
            "color": [255, 0, 0],
        })
    return arcs

all_arcs = []
for fname, ydata in load_yaml_files():
    all_arcs.extend(extract_arcs(ydata, fname))

if all_arcs:
    layer = pdk.Layer(
        "ArcLayer",
        data=all_arcs,
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
else:
    st.info("No offshore transactions with valid coordinates to display.")