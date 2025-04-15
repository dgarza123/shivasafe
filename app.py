import streamlit as st
st.set_page_config(page_title="ShivaSafe Viewer", layout="wide")

import os
import yaml
import pydeck as pdk
from datetime import datetime
from hawaii_db import get_coordinates_by_tmk

EVIDENCE_DIR = "evidence"
DEFAULT_COORDS = [21.3069, -157.8583]

st.title("🌐 ShivaSafe Viewer")
st.markdown("This is a public forensic viewer for extracted land transactions, including offshore flows, parcel history, and affidavit reports.")

# === Map Viewer Section ===
st.subheader("📍 Offshore Transaction Map")

def load_yaml_pairs():
    pairs = []
    for fname in os.listdir(EVIDENCE_DIR):
        if fname.endswith("_entities.yaml"):
            try:
                with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict) and "transactions" in data:
                    pairs.append((fname, data))
            except:
                pass
    return pairs

def extract_lines(yaml_data, filename):
    lines = []
    for tx in yaml_data.get("transactions", []):
        if not isinstance(tx, dict) or "offshore_note" not in tx:
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

if all_lines:
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
else:
    st.info("No offshore arcs to display.")

# === Timeline Section ===
st.subheader("📅 Transaction Timeline")

def load_timeline():
    timeline = []
    for fname in sorted(os.listdir(EVIDENCE_DIR)):
        if fname.endswith("_entities.yaml"):
            path = os.path.join(EVIDENCE_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                for tx in data.get("transactions", []):
                    tmk = str(tx.get("parcel_id", "")).strip()
                    coords = get_coordinates_by_tmk(tmk) or DEFAULT_COORDS
                    timeline.append({
                        "file": data.get("document", fname.replace("_entities.yaml", ".pdf")),
                        "grantor": tx.get("grantor", ""),
                        "grantee": tx.get("grantee", ""),
                        "amount": tx.get("amount", ""),
                        "parcel": tmk,
                        "valid": tx.get("parcel_valid", True),
                        "registry": tx.get("registry_key", ""),
                        "coords": coords,
                        "timestamp": datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d")
                    })
            except:
                continue
    return timeline

timeline = load_timeline()
if not timeline:
    st.info("No timeline data available.")
else:
    for tx in timeline:
        st.markdown(f"#### {tx['file']} ({tx['timestamp']})")
        st.markdown(f"- **Grantor**: {tx['grantor']}")
        st.markdown(f"- **Grantee**: {tx['grantee']}")
        st.markdown(f"- **Amount**: {tx['amount']}")
        st.markdown(f"- **Parcel**: `{tx['parcel']}`")
        st.markdown(f"- **Valid**: {'✅' if tx['valid'] else '❌'}")
        if tx['registry']:
            st.markdown(f"- **Registry Key**: `{tx['registry']}`")
        st.markdown(f"- **Coordinates**: `{tx['coords'][0]:.5f}, {tx['coords'][1]:.5f}`")
        st.markdown("---")

# === Report Access ===
st.subheader("📦 Download Reports")
st.markdown("Visit the [🧾 Download Reports](download_reports) page to generate and download all affidavit reports in ZIP format.")
