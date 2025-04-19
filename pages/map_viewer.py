# pages/map_viewer.py

import streamlit as st
import pandas as pd
import pydeck as pdk

def classify_color(row):
    if "Suppressed" in row["classification"]:
        return [255, 0, 0]       # Red
    elif "Vanished" in row["classification"]:
        return [255, 200, 0]     # Yellow
    elif "Still Public" in row["classification"]:
        return [0, 255, 0]       # Green
    elif "Fabricated" in row["classification"]:
        return [50, 50, 50]      # Black
    else:
        return [120, 120, 120]   # Gray

def run():
    st.title("🧭 TMK Suppression Heatmap")
    st.markdown("""
    This map shows parcels that disappeared from public land records between 2018 and 2025.

    Dot colors represent different types of suppression:

    - 🔴 **Suppressed After Use**
    - 🟡 **Vanished After Use**
    - 🟢 **Still Public**
    - ⚫️ **Fabricated / Never Listed**
    """)

    # load your pre‑built CSV; adjust path if needed
    try:
        df = pd.read_csv("Hawaii_tmk_suppression_status.csv")
    except Exception as e:
        st.error(f"Failed to load suppression CSV: {e}")
        return

    df["color"] = df.apply(classify_color, axis=1)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[Longitude, Latitude]',
        get_fill_color="color",
        get_radius=1000,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=21.3,
        longitude=-157.85,
        zoom=9,
        pitch=0,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>TMK:</b> {TMK}<br><b>Status:</b> {classification}"
        }
    ))
