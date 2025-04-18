# File: pages/timeline.py

import os
import re
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Parcel Disappearance Timeline", layout="wide")
st.title("📈 Parcel Disappearance Timeline")

# ————————————————————————————————
# 1) Discover all HawaiiYYYY.csv files in data/
# ————————————————————————————————
year_files = {}
for fname in os.listdir("data"):
    if fname.lower().startswith("hawai") and fname.lower().endswith(".csv"):
        m = re.search(r"(\d{4})", fname)
        if m:
            year = int(m.group(1))
            year_files[year] = os.path.join("data", fname)

if not year_files:
    st.error("❌ No files like Hawaii2020.csv, Hawaii2021.csv, etc., found in /data.")
    st.stop()

# Sort years
years = sorted(year_files.keys())
baseline = years[0]

st.sidebar.header("Timeline Settings")
st.sidebar.markdown(f"• **Baseline year (year 0):** {baseline}")
st.sidebar.markdown(f"• **Comparisons:** {', '.join(map(str, years[1:]))}")

# ————————————————————————————————
# 2) Load parcel_id sets for each year
# ————————————————————————————————
parcel_sets = {}
for yr, path in year_files.items():
    try:
        df_year = pd.read_csv(path, dtype=str)
    except Exception as e:
        st.error(f"❌ Failed to load `{path}`: {e}")
        st.stop()
    # Find the column containing the parcel/T MK
    tmk_col = next((c for c in df_year.columns if c.lower().strip() in ("tmk", "parcel_id")), None)
    if not tmk_col:
        st.error(f"❌ `{path}` is missing a 'TMK' or 'parcel_id' column.")
        st.stop()
    parcel_sets[yr] = set(df_year[tmk_col].astype(str).str.strip())

# ————————————————————————————————
# 3) Compute disappearance counts vs baseline
# ————————————————————————————————
baseline_set = parcel_sets[baseline]
timeline = []
for yr in years:
    current = parcel_sets[yr]
    disappeared = baseline_set - current
    timeline.append({"year": yr, "disappeared_count": len(disappeared)})

df_timeline = pd.DataFrame(timeline)

# ————————————————————————————————
# 4) Render the line + point chart
# ————————————————————————————————
st.markdown(f"### Parcels from **{baseline}** that have disappeared over time")
chart = pd.DataFrame({
    "Disappeared": df_timeline["disappeared_count"]
}, index=df_timeline["year"])
st.line_chart(chart, use_container_width=True)

# ————————————————————————————————
# 5) Show the data table
# ————————————————————————————————
st.markdown("#### Raw Numbers")
st.dataframe(df_timeline.set_index("year"))

# ————————————————————————————————
# 6) Summary info
# ————————————————————————————————
st.info(
    f"• Baseline ({baseline}): {len(baseline_set)} parcels\n"
    f"• Latest ({years[-1]}): {df_timeline.loc[df_timeline['year'] == years[-1], 'disappeared_count'].values[0]} disappeared"
)
