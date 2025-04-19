# app.py

import os
import sqlite3
import pandas as pd
import streamlit as st
import gdown
from streamlit_folium import st_folium
import folium

# ─── CONFIG ────────────────────────────────────────────────────
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Google Drive IDs
DB_ID  = "1QeV0lIlcaTUAp6O7OJGBtzagpQ_XJc1h"
SUP_ID = "1_Q3pT2sNF3nfCUzWyzBQF5u7lcy-q122"

# Direct download URLs
DB_URL  = f"https://drive.google.com/uc?export=download&id={DB_ID}"
SUP_URL = f"https://drive.google.com/uc?export=download&id={SUP_ID}"

DB_LOCAL  = os.path.join(DATA_DIR, "hawaii.db")
SUP_LOCAL = os.path.join(DATA_DIR, "suppression_status.csv")


def download_if_missing(url: str, path: str, desc: str):
    """Download from Drive if we don’t already have it."""
    if not os.path.exists(path):
        st.info(f"Downloading {desc}…")
        gdown.download(url, path, quiet=False)


@st.cache_data(show_spinner=False)
def load_and_persist_suppression():
    """Fetch suppression CSV, drop & recreate its table in the DB."""
    download_if_missing(SUP_URL, SUP_LOCAL, "suppression CSV")
    sup = pd.read_csv(SUP_LOCAL, dtype=str)

    download_if_missing(DB_URL, DB_LOCAL, "SQLite database")

    # Write suppression_status into the DB, in its own short‑lived connection
    with sqlite3.connect(DB_LOCAL) as conn:
        # enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("DROP TABLE IF EXISTS suppression_status;")
        sup.to_sql(
            name="suppression_status",
            con=conn,
            if_exists="replace",
            index=False,
            dtype={"parcel_id": "TEXT", "status": "TEXT"},
        )

    return sup


@st.cache_data(show_spinner=False)
def load_parcel_data():
    """Read parcels JOINed with suppression_status from the DB."""
    with sqlite3.connect(DB_LOCAL) as conn:
        df = pd.read_sql(
            """
            SELECT 
              p.parcel_id,
              CAST(p.latitude  AS REAL) AS lat,
              CAST(p.longitude AS REAL) AS lon,
              COALESCE(s.status, 'unknown') AS status
            FROM parcels p
            LEFT JOIN suppression_status s USING(parcel_id)
            """,
            conn,
        )
    return df


def main():
    st.set_page_config(page_title="Hawaii TMK Map")
    st.title("📍 Hawaii TMK Suppression Map")

    # 1) Ensure suppression_status is in the DB.
    load_and_persist_suppression()

    # 2) Load the joined parcel+status
    df = load_parcel_data()

    # 3) Render Folium map
    m = folium.Map(location=[21.3069, -157.8583], zoom_start=10)
    colors = {"suppressed": "red", "active": "green", "unknown": "gray"}

    for _, row in df.iterrows():
        if pd.isna(row.lat) or pd.isna(row.lon):
            continue
        folium.CircleMarker(
            location=(row.lat, row.lon),
            radius=3,
            color=colors.get(row.status, "blue"),
            fill=True,
            fill_opacity=0.7,
        ).add_to(m)

    st_folium(m, width=800, height=600)


if __name__ == "__main__":
    main()
