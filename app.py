# app.py
import sqlite3
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

@st.cache_resource
def load_data(db_path: str, csv_path: str):
    # 1) load parcels with lat/lon
    conn = sqlite3.connect(db_path)
    parcels = pd.read_sql_query(
        "SELECT parcel_id, latitude, longitude FROM parcels",
        conn,
        dtype={"parcel_id": str}
    )
    # 2) load suppression status
    status = pd.read_csv(csv_path, dtype={"parcel_id": str, "suppression_status": str})
    conn.close()
    # 3) join them
    df = parcels.merge(status, on="parcel_id", how="left").fillna("unknown")
    # cast lat/lon to floats
    df["latitude"]  = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)
    return df

def build_map(df: pd.DataFrame):
    # center map on average coords
    center = [df.latitude.mean(), df.longitude.mean()]
    m = folium.Map(location=center, zoom_start=8, tiles="CartoDB positron")
    # draw each parcel as a tiny circle colored by status
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
    # add a legend
    legend_html = """
     <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: 120px; height: 80px; 
                 background: white; z-index:9999; padding: 10px; border:2px solid gray;">
       <b>Suppression</b><br>
       <i style="color:red;">●</i> suppressed<br>
       <i style="color:blue;">●</i> not suppressed<br>
       <i style="color:gray;">●</i> unknown
     </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    return m

def main():
    st.set_page_config(page_title="Hawaii TMK Map", layout="wide")
    st.title("📍 Hawaii TMK Suppression Map")

    DB_PATH  = "data/hawaii.db"
    CSV_PATH = "data/Hawaii_tmk_suppression_status.csv"

    st.info(f"Loading data from `{DB_PATH}` and `{CSV_PATH}`…")
    df = load_data(DB_PATH, CSV_PATH)

    st.write(f"Total parcels: **{len(df):,}**")
    st.write("Red = suppressed; Blue = not suppressed; Gray = no data.")

    m = build_map(df)
    st_folium(m, width=900, height=600)

if __name__ == "__main__":
    main()