import streamlit as st
import pandas as pd
import pydeck as pdk

def render_transaction_map(entities):
    points = []
    for e in entities:
        if "parcel_address" in e:
            # Assume geocoded lat/lon from parcel
            points.append({
                "name": e.get("beneficiary") or e.get("grantee"),
                "amount": e.get("amount"),
                "address": e["parcel_address"],
                "lat": e.get("lat", 21.3),  # replace with actual geo
                "lon": e.get("lon", -157.8)
            })

    df = pd.DataFrame(points)
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(latitude=21.3, longitude=-157.8, zoom=7),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position='[lon, lat]',
                get_radius=2500,
                get_fill_color='[200, 30, 0, 160]',
                pickable=True,
            )
        ],
        tooltip={"text": "{name}\n{amount}\n{address}"}
    ))
