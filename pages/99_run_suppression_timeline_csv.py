import streamlit as st
import pandas as pd
import os
import yaml

st.set_page_config(page_title="📊 Rebuild TMK Suppression Timeline", layout="wide")
st.title("📊 TMK Suppression Timeline Generator")

data_dir = "data"
yaml_dir = "evidence"
output_csv = os.path.join(data_dir, "tmk_suppression_timeline.csv")

# === Helper: Normalize GIS TMK format ===
def normalize_tmk(row):
    try:
        zone = str(int(row["zone"]))
        section = str(int(row["section"]))
        plat = str(int(row["plat"]))
        parcel = str(int(row["parcel"]))
        return f"{zone}-{section}-{plat}:{parcel}"
    except:
        return None

# === Load and normalize each year ===
def load_and_normalize(filename):
    path = os.path.join(data_dir, filename)
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df["tmk_normalized"] = df.apply(normalize_tmk, axis=1)
    return set(df["tmk_normalized"].dropna().str.strip())

st.markdown("🔄 Loading GIS data files...")
try:
    tmk_2018 = load_and_normalize("Hawaii2018.csv")
    tmk_2022 = load_and_normalize("Hawaii2022.csv")
    tmk_2025 = load_and_normalize("Hawaii2025.csv")
    st.success("✅ GIS datasets loaded and normalized.")
except Exception as e:
    st.error(f"❌ Failed to load GIS datasets: {e}")
    st.stop()

# === Load all YAML TMKs ===
st.markdown("📥 Scanning YAML files in `/evidence`...")
tmk_to_source = {}
for fname in os.listdir(yaml_dir):
    if not fname.endswith("_entities.yaml"):
        continue
    try:
        with open(os.path.join(yaml_dir, fname), "r") as f:
            ydata = yaml.safe_load(f)
        cert_id = fname.replace("_entities.yaml", "")
        for tx in ydata.get("transactions", []):
            tmk = str(tx.get("parcel_id", "")).strip()
            if tmk:
                tmk_to_source[tmk] = {
                    "certificate": cert_id,
                    "yaml_file": fname
                }
    except Exception as e:
        st.warning(f"⚠️ Could not read {fname}: {e}")

if not tmk_to_source:
    st.error("❌ No TMKs found in YAML files.")
    st.stop()

# === Analyze suppression status ===
st.markdown("🔍 Analyzing suppression timeline...")
rows = []
for tmk, meta in tmk_to_source.items():
    found_2018 = tmk in tmk_2018
    found_2022 = tmk in tmk_2022
    found_2025 = tmk in tmk_2025

    if found_2018 and found_2022 and not found_2025:
        status = "Disappeared"
    elif not found_2018 and found_2022 and not found_2025:
        status = "Erased"
    elif not found_2018 and not found_2022 and not found_2025:
        status = "Fabricated"
    else:
        status = "Public"

    rows.append({
        "TMK": tmk,
        "certificate": meta["certificate"],
        "yaml_file": meta["yaml_file"],
        "found_2018": found_2018,
        "found_2022": found_2022,
        "found_2025": found_2025,
        "status": status
    })

# === Save and show result ===
df_out = pd.DataFrame(rows)
df_out.to_csv(output_csv, index=False)

st.success(f"✅ Suppression timeline saved to: `{output_csv}`")
st.markdown(f"**Rows written:** `{len(df_out)}`")
st.dataframe(df_out)
