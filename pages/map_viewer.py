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
                try:
                    with open(os.path.join(TMP_DIR, fname), "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data:  # ✅ Skip if None
                            pairs.append((pdf, data))
                except Exception as e:
                    st.warning(f"Error reading {fname}: {e}")
    return pairs

def extract_lines(yaml_data):
    lines = []
    txs = yaml_data.get("transactions", [])
    for tx in txs:
        if "offshore_note" not in tx:
            continue
        dest = get_philippines_coords()
        label_parts = [
            tx.get("grantee", "—"),
            tx.get("amount", ""),
            tx.get("parcel_id", ""),
        ]
        if not tx.get("parcel_valid", True):
            label_parts.append("❌ Invalid_
