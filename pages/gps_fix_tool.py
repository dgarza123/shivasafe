import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="GPS Fix Tool", layout="wide")
st.title("📍 GPS Fix Assistant for Parcel Records")

MISSING_GPS_PATH = "missing_gps.csv"
TMK_MASTER_PATH = "data/Hawaii_tmk_master.csv"
OUTPUT_CSV = "gps_patch.csv"

# Load missing_gps.csv
if not os.path.exists(MISSING_GPS_PATH):
    st.error(f"❌ Missing required file: {MISSING_GPS_PATH}")
    st.stop()

df_missing = pd.read_csv(MISSING_GPS_PATH)
st.success(f"✅ Loaded {len(df_missing)} missing GPS records.")

# Load TMK master file
use_autofill = False
if os.path.exists(TMK_MASTER_PATH):
    use_autofill = st.checkbox("🧭 Auto-fill GPS from TMK reference (Hawaii_tmk_master.csv)")
    if use_autofill:
        df_ref = pd.read_csv(TMK_MASTER_PATH)
        df_ref = df_ref.rename(columns={col: col.lower() for col in df_ref.columns})
        df_ref = df_ref.rename(columns={"tmk": "parcel_id"}) if "tmk" in df_ref.columns else df_ref
        df_ref = df_ref[["parcel_id", "latitude", "longitude"]]
        df_ref["parcel_id"] = df_ref["parcel_id"].astype(str).str.strip()
else:
    st.warning("⚠️ TMK master file not found at: data/Hawaii_tmk_master.csv")

# Create editable copy
df_missing["latitude"] = None
df_missing["longitude"] = None
df_missing["source"] = ""

# Apply TMK autofill if enabled
if use_autofill:
    matches = 0
    for i, row in df_missing.iterrows():
        pid = str(row["parcel_id"]).strip()
        ref = df_ref[df_ref["parcel_id"] == pid]
        if not ref.empty:
            df_missing.at[i, "latitude"] = ref.iloc[0]["latitude"]
            df_missing.at[i, "longitude"] = ref.iloc[0]["longitude"]
            df_missing.at[i, "source"] = "TMK match"
            matches += 1
    st.success(f"📍 Auto-filled {matches} records from TMK master.")

st.markdown("### 📝 Manual GPS Fixes (optional)")
for i, row in df_missing.iterrows():
    col1, col2, col3, col4 = st.columns([2, 2, 3, 3])
    with col1:
        st.text(row["certificate_id"])
    with col2:
        st.text(row["parcel_id"])
    with col3:
        lat = st.text_input(f"Lat for {row['parcel_id']}", value=str(row["latitude"]) if pd.notnull(row["latitude"]) else "", key=f"lat_{i}")
    with col4:
        lon = st.text_input(f"Lon for {row['parcel_id']}", value=str(row["longitude"]) if pd.notnull(row["longitude"]) else "", key=f"lon_{i}")

    # Update DataFrame
    try:
        df_missing.at[i, "latitude"] = float(lat.strip()) if lat.strip() else None
        df_missing.at[i, "longitude"] = float(lon.strip()) if lon.strip() else None
        if lat.strip() and lon.strip() and not df_missing.at[i, "source"]:
            df_missing.at[i, "source"] = "Manual"
    except:
        st.warning(f"⚠️ Invalid GPS for {row['parcel_id']} — not saved")

# Filter to rows with filled GPS
df_patch = df_missing.dropna(subset=["latitude", "longitude"])

st.markdown("### ✅ Preview of Patch File")
st.dataframe(df_patch[["certificate_id", "parcel_id", "latitude", "longitude", "source"]])

# Save fix-up file
df_patch.to_csv(OUTPUT_CSV, index=False)
st.download_button("⬇️ Download GPS Patch CSV", data=df_patch.to_csv(index=False), file_name=OUTPUT_CSV, mime="text/csv")

st.info(f"💾 Patch file includes {len(df_patch)} rows with fixed GPS coordinates.")
