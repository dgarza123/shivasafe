# pages/map_compare.py
import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk

st.set_page_config(page_title="Suppression Map Compare", layout="wide")
st.title("Map of Suppressed vs Public Parcels")

# Load from database
conn = sqlite3.connect("data/hawaii.db")
df = pd.read_sql_query("SELECT * FROM parcels WHERE status != 'Fabricated'", conn)
conn.close()

# Drop entries without coordinates
df = df.dropna(subset=["latitude", "longitude"])

# Assign color
def classify(row):
    if row["status"] == "Disappeared":
        return [255, 0, 0]  # red
    elif row["status"] == "Public":
        return [0, 100, 255]  # blue
    else:
        return [200, 200, 200]

df["color"] = df.apply(classify, axis=1)

# Render pydeck map
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=20.7,
        longitude=-157.5,
        zoom=6.5,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position="[longitude, latitude]",
            get_fill_color="color",
            get_radius=500,
            pickable=True,
            opacity=0.7,
        )
    ],
    tooltip={
        "text": "Parcel: {parcel_id}\nCertificate: {certificate_id}\nGrantee: {grantee}\nStatus: {status}"
    }
))
