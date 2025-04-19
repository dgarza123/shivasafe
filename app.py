# app.py
import sqlite3
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

@st.cache_resource
def load_data(db_path: str, csv_path: str):
    conn = sqlite3.connect(db_path)
    parcels = pd.read_sql_query(
        "SELECT parcel_id, latitude, longitude FROM parcels",
        conn,
        dtype={"parcel_id": str}
    )
    status = pd.read_csv(csv_path, dtype={"parcel_id": str, "suppression_status": str})
    conn.close()
    df = parcels.merge(status, on="parcel_id", how="left").fillna("unknown")
    df["latitude"]  = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    return df

def build_map(df: pd.DataFrame):
    # Center on the mean location
    center = [df.latitude.mean(), df.longitude.mean()]
    m = folium.Map(location=center, zoom_start=8, tiles="CartoDB positron")

    # Plot each point
    for _, row in df.iterrows():
        color = {
            "True":  "red",
            "False": "blue"
        }.get(row.suppression_status, "gray")
        folium.CircleMarker(
            location=(row.latitude, row.longitude),
            radius=2,
            color=color,
            fill=True,
            fill_opacity=0.7,
        ).add_to(m)

    # Legend HTML — all of this is inside a single triple‑quoted string
    legend_html = """
<div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 140px;
    height: 100px;
    background-color: white;
    border: 2px solid gray;
    z-index: 9999;
    padding: 8px;
    font-size: 12px;
">
  <b>Suppression</b><br>
  <span style="color:red;">●</span> suppressed<br>
  <span style="color:blue;">●</span> not suppressed<br>
  <span style="color:gray;">●</span> unknown
</div>
"""
    # Attach the legend
    m.get_root().html.add_child(folium.Element(legend_html))
    return m

def main():
    st.set_page_config(page_title="Hawaii TMK Map", layout="wide")
    st.title("📍 Hawaii TMK Suppression Map")

    DB_PATH  = "data/hawaii.db"
    CSV_PATH = "data/Hawaii_tmk_suppression_status.csv"

    st.info(f"Loading `{DB_PATH}` + `{CSV_PATH}`…")
    df = load_data(DB_PATH, CSV_PATH)

    st.write(f"Total parcels: **{len(df):,}**")
    st.write("Red = suppressed · Blue = not suppressed · Gray = unknown")

    m = build_map(df)
    st_folium(m, width=900, height=600)

if __name__ == "__main__":
    main()