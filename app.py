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

# Your Drive file IDs
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


@st.cache_data(show_spinner=False)
def load_and_persist_suppression():
    download_if_missing(SUP_URL, SUP_LOCAL, "suppression CSV")
    sup = pd.read_csv(SUP_LOCAL, dtype=str)

    download_if_missing(DB_URL, DB_LOCAL, "SQLite database")

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
    return sup


@st.cache_data(show_spinner=False)
def load_parcel_data():
    download_if_missing(DB_URL, DB_LOCAL, "SQLite database")

    with sqlite3.connect(DB_LOCAL) as conn:
        # show what tables actually exist
        tables = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()]
        if "parcels" not in tables:
            st.error(
                "❌ I looked inside your database and I don’t see a `parcels` table.\n\n"
                f"Tables found: {tables}\n\n"
                "Please double‐check that you’ve supplied the right DB file."
            )
            return pd.DataFrame(columns=["parcel_id","lat","lon","status"])

        # if it exists, pull it
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
    st.set_page_config(page_title="Hawaii TMK Map", layout="wide")
    st.title("📍 Hawaii TMK Suppression Map")

    # ensure we have the suppression table
    load_and_persist_suppression()

    # load parcels + status (or empty DF on error)
    df = load_parcel_data()
    if df.empty:
        st.warning("No parcel data to show.")
        return

    # build map
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
