import os
import sqlite3

import pandas as pd
import streamlit as st


def run():
    st.title("🔍 TMK Checker")

    # ——— 1) get TMK input ——————————————————————————————
    tmk = st.text_input("Enter TMK (e.g. 389014053):", "")
    if not tmk:
        st.info("Type or paste a TMK above to begin.")
        return

    # ——— 2) load suppression status CSV ————————————————
    supp_csv = os.path.join("data", "Hawaii_tmk_suppression_status.csv")
    try:
        df_supp = pd.read_csv(supp_csv, dtype={"TMK": str})
    except Exception as e:
        st.error(f"❌ Could not load suppression CSV at `{supp_csv}`:\n{e}")
        return

    # filter for this TMK
    record = df_supp[df_supp["TMK"] == tmk]
    if record.empty:
        st.warning(f"No suppression record found for TMK **{tmk}**.")
    else:
        st.subheader("Suppression Status")
        st.table(record)

    # ——— 3) look up coordinates in SQLite DB ————————————
    db_path = os.path.join("data", "hawaii.db")
    if not os.path.exists(db_path):
        st.info("ℹ️ Database not found at `data/hawaii.db`.")
        return

    try:
        conn = sqlite3.connect(db_path)
        coords = pd.read_sql_query(
            "SELECT latitude, longitude FROM parcels WHERE parcel_id = ?",
            conn,
            params=(tmk,),
        )
    except Exception as e:
        st.error(f"❌ Error querying database:\n{e}")
        return
    finally:
        conn.close()

    if coords.empty:
        st.info("No coordinate found in the DB for this TMK.")
    else:
        lat = coords.at[0, "latitude"]
        lon = coords.at[0, "longitude"]
        st.subheader("Location")
        st.write(f"**Latitude:** {lat:.6f}   •   **Longitude:** {lon:.6f}")

        # show a simple map
        st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
