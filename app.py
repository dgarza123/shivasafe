# app.py

import os
import sqlite3
import pandas as pd
import streamlit as st
import gdown
from streamlit_folium import st_folium
import folium

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Google Drive file IDs
DB_ID  = "1QeV0lIlcaTUAp6O7OJGBtzagpQ_XJc1h"
SUP_ID = "1_Q3pT2sNF3nfCUzWyzBQF5u7lcy-q122"

DB_URL  = f"https://drive.google.com/uc?export=download&id={DB_ID}"
SUP_URL = f"https://drive.google.com/uc?export=download&id={SUP_ID}"

DB_LOCAL  = os.path.join(DATA_DIR, "hawaii.db")
SUP_LOCAL = os.path.join(DATA_DIR, "suppression_status.csv")


def download_if_missing(url: str, path: str, desc: str):
    if not os.path.exists(path):
        st.info(f"⏬ Downloading {desc}…")
        gdown.download(url, path, quiet=False)


@st.cache_data
def prepare_db():
    # 1) Download CSV & DB if needed
    download_if_missing(SUP_URL, SUP_LOCAL, "suppression CSV")
    download_if_missing(DB_URL, DB_LOCAL, "SQLite DB")

    # 2) Load suppression status into the DB
    sup = pd.read_csv(SUP_LOCAL, dtype=str)
    with sqlite3.connect(DB_LOCAL) as conn:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("DROP TABLE IF EXISTS suppression_status;")
        sup.to_sql(
            name="suppression_status",
            con=conn,
            if_exists="replace",
            index=False,
            dtype={"parcel_id": "TEXT", "status": "TEXT"},
        )


@st.cache_data
def load_master_with_status():
    with sqlite3.connect(DB_LOCAL) as conn:
        # what tables exist?
        tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        )}
        # if our master is missing, bail
        master = "Hawaii_tmk_master"
        if master not in tables:
            st.error(f"❌ Table `{master}` not found. Available: {sorted(tables)}")
            return pd.DataFrame([], columns=["parcel_id","lat","lon","status"])

        # pull from master + status
        df = pd.read_sql(
            f"""
            SELECT
              m.parcel_id,
              CAST(m.latitude  AS REAL) AS lat,
              CAST(m.longitude AS REAL) AS lon,
              COALESCE(s.status, 'unknown') AS status
            FROM "{master}" m
            LEFT JOIN suppression_status s USING(parcel_id)
            """,
            conn,
        )
    return df


def main():
    st.set_page_config(page_title="Hawaii TMK Map", layout="wide")
    st.title("📍 Hawaii TMK Suppression Map")

    # Download & prepare
    prepare_db()

    # Load the parcel master + status
    df = load_master_with_status()
    if df.empty:
        st.warning("No data to display.")
        return

    # Build a simple Folium map
    m = folium.Map(location=[21.3069, -157.8583], zoom_start=10)
    colors = {"suppressed": "red", "active": "green", "unknown": "gray"}

    for _, r in df.iterrows():
        if pd.isna(r.lat) or pd.isna(r.lon):
            continue
        folium.CircleMarker(
            location=(r.lat, r.lon),
            radius=3,
            color=colors.get(r.status, "blue"),
            fill=True,
            fill_opacity=0.6,
        ).add_to(m)

    st_folium(m, width=800, height=600)


if __name__ == "__main__":
    main()
