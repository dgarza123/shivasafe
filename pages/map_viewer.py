import streamlit as st
import sqlite3
import yaml
import os
import pydeck as pdk

st.set_page_config(page_title="Map Viewer", layout="wide")
st.title("🗺️ TMK Suppression + Offshore Flow Map")

# Constants
DEFAULT_LAT, DEFAULT_LON = 21.3069, -157.8583
EVIDENCE_DIR = "evidence"

# DB connection
@st.cache_data
def load_suppression_data():
    conn = sqlite3.connect("Hawaii.db")
    df = pd.read_sql_query("SELECT * FROM tmk_suppression_status", conn)
    conn.close()
    return df

# YAML-based arcs
def extract_transaction_arcs():
    arcs = []
    for fname in os.listdir(EVIDENCE_DIR):
        if fname.endswith("_entities.yaml"):
            with open(os.path.join(EVIDENCE_DIR, fname), "r", encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                    doc = data.get("document", fname.replace("_entities.yaml", ".pdf"))
                    sha = data.get("sha256", "")
                    for tx in data.get("transactions", []):
                        if not isinstance(tx, dict):
                            continue
                        tmk = str(tx.get("parcel_id", "")).strip()
                        coords = get_coords_by_tmk(tmk)
                        if coords and "country" in tx:
                            arcs.append({
                                "from_lat": coords[0],
                                "from_lon": coords[1],
                                "to_lat": offshore_coords(tx["country"])[0],
                                "to_lon": offshore_coords(tx["country"])[1],
                                "label": f"{tx.get('amount', '')} to {tx.get('country', '')}",
                                "tmk": tmk,
                                "grantee": tx.get("grantee", ""),
                                "cert_id": tx.get("cert_id", ""),
                                "link": tx.get("link", ""),
                                "document": doc
                            })
                except:
                    continue
    return arcs

# Get offshore coordinates by country (simple lookup)
def offshore_coords(country):
    lookup = {
        "Philippines": (13.41, 122.56),
        "Switzerland": (46.8, 8.2),
        "Singapore": (1.35, 103.8)
    }
    return lookup.get(country, (13.0, 120.0))  # Default to PH-like location

# TMK to lat/lon
@st.cache_data
def get_coords_by_tmk(tmk):
    conn = sqlite3.connect("Hawaii.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Latitude, Longitude FROM tmk_lookup WHERE TMK=?", (tmk,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return (row[0], row[1])
    return None

# === UI Toggle ===
view_mode = st.radio("Select Map Layer", ["Suppression Dots", "Offshore Arcs"], horizontal=True)

# === View 1: Suppression Dots ===
if view_mode == "Suppression Dots":
    df = load_suppression_data()

    color_map = {
        "Suppressed After Use": [255, 0, 0],
        "Vanished After Use": [255, 165, 0],
        "Still Public": [0, 200, 0],
        "Fabricated?": [150, 150, 150]
    }
    df["color"] = df["classification"].apply(lambda x: color_map.get(x, [100, 100, 100]))
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[Longitude, Latitude]',
        get_color="color",
        get_radius=180,
        pickable=True
    )
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(latitude=DEFAULT_LAT, longitude=DEFAULT_LON, zoom=10),
        tooltip={
            "html": "<b>TMK:</b> {TMK}<br>"
                    "<b>Status:</b> {classification}<br>"
                    "<b>Doc:</b> {document}<br>"
                    "<b>SHA:</b> {sha256}"
        }
    ))

# === View 2: Offshore Arcs ===
elif view_mode == "Offshore Arcs":
    arcs = extract_transaction_arcs()
    if not arcs:
        st.warning("No offshore transactions found in YAMLs.")
    else:
        arc_layer = pdk.Layer(
            "ArcLayer",
            data=arcs,
            get_source_position=["from_lon", "from_lat"],
            get_target_position=["to_lon", "to_lat"],
            get_source_color=[200, 0, 0],
            get_target_color=[0, 100, 255],
            get_width=3,
            pickable=True,
            auto_highlight=True
        )
        st.pydeck_chart(pdk.Deck(
            layers=[arc_layer],
            initial_view_state=pdk.ViewState(latitude=DEFAULT_LAT, longitude=DEFAULT_LON, zoom=2),
            tooltip={
                "html": "<b>TMK:</b> {tmk}<br>"
                        "<b>To:</b> {label}<br>"
                        "<b>Grantee:</b> {grantee}<br>"
                        "<b>Cert:</b> {cert_id}<br>"
                        "<b>Doc:</b> {document}<br>"
                        "<b>Link:</b> {link}"
            }
        ))