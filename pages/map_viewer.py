import os
import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk

st.set_page_config(page_title="Oʻahu Parcel Sales Map", layout="wide")
st.title("🗺️ Oʻahu Parcel Sales & TMK Suppression Map")

# ————————————————————————————————
# Sidebar: Year selectors & heatmap toggle
# ————————————————————————————————
st.sidebar.header("Map Controls")
# Auto‑discover all your HawaiiYYYY.csv files in /data
year_files = {
    os.path.splitext(f)[0].replace("Hawaii", ""): os.path.join("data", f)
    for f in os.listdir("data")
    if f.startswith("Hawaii") and f.endswith(".csv")
}
years = sorted(year_files.keys())
if len(years) >= 2:
    year1 = st.sidebar.selectbox("Baseline Year", years, index=0)
    year2 = st.sidebar.selectbox("Comparison Year", years, index=len(years)-1)
else:
    year1 = year2 = years[0] if years else None

show_heat = st.sidebar.checkbox("Overlay Heatmap", False)

# ————————————————————————————————
# Load your transactions database
# ————————————————————————————————
DB_PATH = "data/hawaii.db"
if not os.path.exists(DB_PATH):
    st.error("❌ Database not found at data/hawaii.db. Please rebuild it first.")
    st.stop()

conn = sqlite3.connect(DB_PATH)
df_all = pd.read_sql_query("SELECT * FROM parcels", conn)
conn.close()

# Drop any rows without valid numeric GPS
df = (
    df_all
    .dropna(subset=["latitude","longitude"])
    .loc[lambda d: d.latitude.apply(lambda x: isinstance(x,(int,float)))
                  & d.longitude.apply(lambda x: isinstance(x,(int,float)))]
)

if df.empty:
    st.warning("⚠️ No parcels with valid GPS found.")
    st.stop()

# ————————————————————————————————
# Show counts for debugging
# ————————————————————————————————
st.markdown(f"**Total parcels in DB:** {len(df_all)}   •  **Shown on map:** {len(df)}")

# ————————————————————————————————
# Classify by “disappeared” status between years
# ————————————————————————————————
if year1 and year2 and year1 != year2:
    try:
        y1 = pd.read_csv(year_files[year1], dtype=str)
        y2 = pd.read_csv(year_files[year2], dtype=str)
        set1 = set(y1["parcel_id"].str.strip())
        set2 = set(y2["parcel_id"].str.strip())
        def compare(pid):
            pid = pid.strip()
            if pid in set1 and pid not in set2:
                return "Disappeared"
            if pid in set2:
                return "Public"
            return "Unknown"
        df["year_status"] = df["parcel_id"].apply(compare)
    except Exception as e:
        st.warning(f"⚠️ Failed to load year files: {e}")
        df["year_status"] = df["status"]
else:
    df["year_status"] = df["status"]

# ————————————————————————————————
# Mark DNLR sales
# ————————————————————————————————
df["dnrl_sale"] = df["grantor"].str.contains("DLNR", case=False, na=False)

# ————————————————————————————————
# Decide dot color
# ————————————————————————————————
def pick_color(r):
    if r.dnrl_sale:
        return [255, 0, 0]           # red for DNLR
    if r.year_status == "Disappeared":
        return [255, 200, 0]         # yellow
    if r.year_status == "Public":
        return [0, 200, 0]           # green
    return [160, 160, 160]          # gray fallback

df["color"] = df.apply(pick_color, axis=1)

# ————————————————————————————————
# Layers: optional heat + scatter
# ————————————————————————————————
layers = []
if show_heat:
    layers.append(pdk.Layer(
        "HeatmapLayer", data=df,
        get_position='[longitude, latitude]',
        get_weight=1
    ))
layers.append(pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[longitude, latitude]',
    get_fill_color="color",
    get_radius=1000,
    pickable=True
))

# ————————————————————————————————
# Tooltip content
# ————————————————————————————————
tooltip = {
    "html": """
    <b>{parcel_id}</b><br/>
    {grantor} → {grantee}<br/>
    Amount: {amount}<br/>
    Status: {year_status}
    """,
    "style": {"backgroundColor":"black","color":"white"}
}

# ————————————————————————————————
# Locked top‑down view of Oʻahu
# ————————————————————————————————
view = pdk.ViewState(
    latitude=21.3049,
    longitude=-157.8577,
    zoom=11,
    pitch=0,
    bearing=0
)

# ————————————————————————————————
# Render the map
# ————————————————————————————————
deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v10",
    initial_view_state=view,
    layers=layers,
    tooltip=tooltip
)
st.pydeck_chart(deck)
