# app.py
import os
import sqlite3
import pandas as pd
import streamlit as st
import gdown
from streamlit_folium import st_folium
import folium

# ─── CONFIG ────────────────────────────────────────────────────
DB_ID   = "1QeV0lIlcaTUAp6O7OJGBtzagpQ_XJc1h"
SUP_ID  = "1_Q3pT2sNF3nfCUzWyzBQF5u7lcy-q122"

DB_URL   = f"https://drive.google.com/uc?export=download&id={DB_ID}"
SUP_URL  = f"https://drive.google.com/uc?export=download&id={SUP_ID}"

os.makedirs("data", exist_ok=True)
DB_LOCAL  = "data/hawaii.db"
SUP_LOCAL = "data/suppression_status.csv"

# ─── DATA LOADING ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_connection():
    if not os.path.exists(DB_LOCAL):
        st.info("Downloading database…")
        gdown.download(DB_URL, DB_LOCAL, quiet=False)
    # **open read‑write** so we can write our suppression table
    return sqlite3.connect(DB_LOCAL)

@st.cache_data(show_spinner=False)
def load_suppression_csv():
    if not os.path.exists(SUP_LOCAL):
        st.info("Downloading suppression CSV…")
        gdown.download(SUP_URL, SUP_LOCAL, quiet=False)
    return pd.read_csv(SUP_LOCAL, dtype=str)

# ─── APP ──────────────────────────────────────────────────────
def main():
    st.title("Hawaii TMK Map")

    conn  = get_connection()
    sup   = load_suppression_csv()

    # inject into the DB so we can join in SQL
    sup.to_sql("suppression_status", conn, if_exists="replace", index=False)

    # pull parcel locations + status
    df = pd.read_sql(
        """
        SELECT 
          p.parcel_id, 
          CAST(p.latitude AS REAL)  AS lat, 
          CAST(p.longitude AS REAL) AS lon,
          COALESCE(s.status, 'unknown') AS status
        FROM parcels p
        LEFT JOIN suppression_status s USING(parcel_id)
        """,
        conn,
    )

    # basic Folium map
    m = folium.Map(location=[21.3069, -157.8583], zoom_start=10)
    # color by status
    colors = {"suppressed":"red","active":"green","unknown":"gray"}
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=(row.lat, row.lon),
            radius=3,
            color=colors.get(row.status, "blue"),
            fill=True,
            fill_opacity=0.7,
        ).add_to(m)

    st_data = st_folium(m, width=800, height=600)


if __name__ == "__main__":
    main()
