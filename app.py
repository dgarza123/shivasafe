import streamlit as st
from pages.timeline import load_transactions
from hawaii_db import get_coordinates_by_tmk
import pydeck as pdk

st.set_page_config(page_title="Shiva PDF", layout="wide")
st.title("Shiva PDF")

# Description
st.markdown("This platform provides a public interface to explore concealed real estate transactions derived from decoded PDF records. Data includes parcel transfers, offshore activity, and entity linkages.")

st.markdown("---")

# Timeline Preview (Latest 5)
st.subheader("Recent Transactions")

timeline = load_transactions()
preview = sorted(timeline, key=lambda x: x["timestamp"], reverse=True)[:5]

for tx in preview:
    st.markdown(f"**{tx['file']}** — {tx['timestamp']}")
    st.markdown(f"- Grantor: {tx['grantor']}")
    st.markdown(f"- Grantee: {tx['grantee']}")
    st.markdown(f"- Amount: {tx['amount']}")
    st.markdown(f"- Parcel ID: {tx['parcel_id']}")
    if tx.get("registry_key"):
        st.markdown(f"- Registry Key: {tx['registry_key']}")
    st.markdown("---")

# Offshore Map Snapshot
st.subheader("Offshore Transfer Snapshot")

lines = []
for tx in timeline:
    if "offshore_note" not in tx:
        continue
    tmk = tx.get("parcel_id", "").strip()
    coords = get_coordinates_by_tmk(tmk)
    if not coords:
        continue
    lines.append({
        "from_lat": coords[0],
        "from_lon": coords[1],
        "to_lat": 13.41,
        "to_lon": 122.56,
        "label": tx["grantee"]
    })

if lines:
    layer = pdk.Layer(
        "ArcLayer",
        data=lines,
        get_source_position=["from_lon", "from_lat"],
        get_target_position=["to_lon", "to_lat"],
        get_source_color=[200, 30, 0],
        get_target_color=[0, 60, 180],
        width_scale=0.0001,
        get_width=30,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=21.3,
        longitude=-157.8,
        zoom=2,
        bearing=0,
        pitch=30,
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

else:
    st.info("No offshore transfers available to display.")