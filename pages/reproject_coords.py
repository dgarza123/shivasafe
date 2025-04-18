# File: pages/reproject_coords.py

import os
import io
import pandas as pd
import streamlit as st
from pyproj import Transformer, CRS

st.set_page_config(page_title="Reproject TMK CSV", layout="centered")
st.title("🗺️ Reproject TMK Master CSV to WGS84")

st.markdown("""
Upload your **projected‐coordinate** CSV (`parcel_id,latitude,longitude`) and its `.prj` (optional).
The app will reproject it into **WGS84 decimal degrees** and let you download the result.
""")

# 1️⃣ Upload files
csv_file = st.file_uploader("Upload projected‑coords CSV", type="csv")
prj_file = st.file_uploader("Upload matching .prj file (optional)", type="prj")

if not csv_file:
    st.info("📄 Please upload your `Hawaii_tmk_master.csv` first.")
    st.stop()

# 2️⃣ Read CSV into DataFrame
try:
    df = pd.read_csv(csv_file, dtype=str)
except Exception as e:
    st.error(f"❌ Failed to read CSV: {e}")
    st.stop()

required = {"parcel_id","latitude","longitude"}
if not required.issubset(df.columns):
    st.error(f"❌ CSV must contain columns {required}. Found: {list(df.columns)}")
    st.stop()

# Convert coords to float
df["latitude"]  = df["latitude"].astype(float)
df["longitude"] = df["longitude"].astype(float)

# 3️⃣ Determine source CRS
src_crs = None
if prj_file:
    try:
        wkt = prj_file.read().decode("utf-8")
        crs0 = CRS.from_wkt(wkt)
        epsg0 = crs0.to_epsg()
        src_crs = f"EPSG:{epsg0}" if epsg0 else crs0.to_string()
        st.success(f"🔎 Detected source CRS: {src_crs}")
    except Exception as e:
        st.warning(f"⚠️ Could not parse .prj: {e}")

if not src_crs:
    epsg_in = st.text_input("Enter EPSG code of input projection", value="3564")
    if not epsg_in.strip().isdigit():
        st.error("❌ Please enter a valid EPSG code (numbers only).")
        st.stop()
    src_crs = f"EPSG:{epsg_in.strip()}"

# 4️⃣ Perform reprojection
if st.button("🚀 Reproject to WGS84"):
    try:
        transformer = Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
        lons, lats = transformer.transform(
            df["longitude"].tolist(),
            df["latitude"].tolist()
        )
        df["longitude"], df["latitude"] = lons, lats
    except Exception as e:
        st.error(f"❌ Reprojection failed: {e}")
        st.stop()

    # 5️⃣ Offer download
    out_buf = io.StringIO()
    df.to_csv(out_buf, index=False)
    out_buf.seek(0)

    st.success("✅ Reprojected successfully!")
    st.download_button(
        "⬇️ Download WGS84 CSV",
        out_buf.getvalue(),
        file_name="Hawaii_tmk_master_wgs84.csv",
        mime="text/csv"
    )
