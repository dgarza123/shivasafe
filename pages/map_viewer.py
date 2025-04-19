import streamlit as st
import pandas as pd
import pydeck as pdk
import os

def run():
    st.title("🧭 TMK Suppression Heatmap")

    csv_path = "data/Hawaii_tmk_suppression_status.csv"
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        st.error(f"CSV not found at `{csv_path}`")
        st.stop()

    # … your existing color logic …

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position="[Longitude, Latitude]",
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
            "html": "<b>TMK:</b> {TMK}<br><b>Status:</b> "
                    "{classification}"
        }
    ))
