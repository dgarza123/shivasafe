# pages/tmk_checker.py

import streamlit as st
import pandas as pd

# point this at your master list of TMKs
KNOWN_TMK_CSV = "Hawaii_tmk_master.csv"

@st.cache_data
def load_known_tmks():
    df = pd.read_csv(KNOWN_TMK_CSV, dtype=str)
    # assume column is named 'TMK' or 'parcel_id'; adjust if different
    key = 'TMK' if 'TMK' in df.columns else 'parcel_id'
    return set(df[key].tolist())

def run():
    st.title("🔍 TMK Checker")
    st.markdown("Enter any TMK to see if it’s in the master list.")

    tmk = st.text_input("TMK (e.g. 389014053)")
    if not tmk:
        return

    known = load_known_tmks()
    if tmk in known:
        st.success(f"✅ TMK **{tmk}** found in master list.")
    else:
        st.error(f"❌ TMK **{tmk}** *not* found.")
