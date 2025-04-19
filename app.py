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
DB_ID = "1QeV0lIlcaTUAp6O7OJGBtzagpQ_XJc1h"      # SQLite DB
SUP_ID = "1_Q3pT2sNF3nfCUzWyzBQF5u7lcy-q122"     # CSV

DB_LOCAL = os.path.join(DATA_DIR, "hawaii.db")
SUP_LOCAL = os.path.join(DATA_DIR, "suppression_status.csv")

def download_if_missing(file_id: str, path: str, desc: str):
    if not os.path.exists(path) or os.path.getsize(path) < 10_000:
        st.info(f"⏬ Downloading {desc}…")
        gdown.download(id=file_id, output=path, quiet=False)

@st.cache_data(show_spinner=False)
def load_master_with_status():
    # 1) Fetch both
    download_if_missing(DB_ID, DB_LOCAL, "SQLite DB")
    download_if_missing(SUP_ID, SUP_LOCAL, "suppression CSV")

    # 2) Connect & (debug) list tables
    with sqlite3.connect(DB_LOCAL) as conn:
        try:
            tables = pd.read_sql(
                "SELECT name FROM sqlite_master WHERE type='table'", conn
            )["name"].tolist()
            st.write("Tables in DB:", tables)
        except Exception as e:
            st.error(f"Failed to list tables: {e}")
            return pd.DataFrame([], columns=["parcel_id","lat","lon","status"])

        # 3) Read your master
        try:
            master = pd.read_sql(
                """
                SELECT
                  parcel_id,
                  CAST(latitude  AS REAL) AS lat,
                  CAST(longitude AS REAL) AS lon
                FROM Hawaii_tmk_master
                """,
                conn,
            )
        except Exception as e:
            st.error(f"Error querying Hawaii_tmk_master: {e}")
            return pd.DataFrame([], columns=["parcel_id","lat","lon","status"])

    # 4) Load CSV & normalize
    sup = pd.read_csv(SUP_LOCAL, dtype=str)
    cols = list(sup.columns)
    if len(cols) < 2:
        st.error("Suppression CSV needs at least two columns (parcel_id + status).")
        return pd.DataFrame([], columns=["parcel_id","lat","lon","status"])
    sup = sup.rename(columns={cols[0]: "parcel_id", cols[1]: "status"})
    sup["status"] = sup["status"].fillna("unknown")

    # 5) Merge
    df = master.merge(sup[["parcel_id","status"]], on="parcel_id", how="left")
    df["status"] = df["status"].fillna("unknown")

    return df

def main():
    st.set_page_config(page_title="Hawaii TMK Map", layout="wide")
    st.title("Hawaii TMK Suppression Map")

    df = load_master_with_status()
    if df.empty:
        st.warning("No data to display.")
        return

    # 6) Folium map
    m = folium.Map(location=[21.3069, -157.8583], zoom_start=10)
    colors = {"suppressed": "red", "active": "green", "unknown": "gray"}
    for _, r in df.iterrows():
        if pd.isna(r.lat) or pd.isna(r.lon):
            continue
        folium.CircleMarker(
            [r.lat, r.lon],
            radius=3,
            color=colors.get(r.status, "blue"),
            fill=True,
            fill_opacity=0.6,
        ).add_to(m)

    st_folium(m, width=800, height=600)

if __name__ == "__main__":
    main()