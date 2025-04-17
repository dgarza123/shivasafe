import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Debug: Check hawaii.db", layout="centered")
st.title("🔍 Debug: What's inside hawaii.db?")

try:
    conn = sqlite3.connect("data/hawaii.db")
    df = pd.read_sql_query("SELECT DISTINCT parcel_id FROM parcels", conn)
    conn.close()

    if df.empty:
        st.warning("⚠️ No parcel_id entries found in hawaii.db.")
    else:
        st.success(f"✅ {len(df)} unique parcel IDs found.")
        st.dataframe(df.head(100))

except Exception as e:
    st.error(f"❌ Could not query hawaii.db: {e}")
