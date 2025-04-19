# pages/data_builder.py
import streamlit as st
import pandas as pd
import yaml, zipfile, io

st.set_page_config(page_title="🔨 Data Builder", layout="wide")
st.title("🔨 Data Builder")

st.markdown("""
Upload your **YAML ZIP**, your **Hawaii_tmk_master.csv**, and your **year CSVs** (e.g. Hawaii2020.csv, …).
Streamlit will then extract GPS and build:

- `gps_patch.csv`  
- `missing_gps.csv`  
- `Hawaii_tmk_suppression_status.csv`  
""")

yaml_zip = st.file_uploader("1️⃣ Upload YAML ZIP", type="zip")
master_csv = st.file_uploader("2️⃣ Upload Hawaii_tmk_master.csv", type="csv")
year_files = st.file_uploader(
    "3️⃣ Upload historical year CSVs (Hawaii2020.csv, …)", 
    type="csv", accept_multiple_files=True
)

if yaml_zip and master_csv and year_files:
    if st.button("▶️ Build all CSVs"):
        # — load master TMK table —
        master_df = pd.read_csv(master_csv, dtype=str)
        master_df["parcel_id"] = master_df["parcel_id"].astype(str)
        master_ids = set(master_df["parcel_id"])

        # — 1) extract all GPS from the YAML ZIP —
        gps_recs = []
        z = zipfile.ZipFile(io.BytesIO(yaml_zip.read()))
        for fn in z.namelist():
            if fn.lower().endswith((".yaml", ".yml")):
                doc = yaml.safe_load(z.read(fn))
                for tx in doc.get("transactions", []):
                    pid = tx.get("parcel_id")
                    gps = tx.get("gps")
                    if pid and gps:
                        gps_recs.append({
                            "parcel_id": str(pid).replace(":", "").replace("-", ""),
                            "latitude": gps[0],
                            "longitude": gps[1]
                        })
        gps_df = pd.DataFrame(gps_recs).drop_duplicates("parcel_id")
        gps_df.to_csv("data/gps_patch.csv", index=False)
        st.success("✅ gps_patch.csv written to data/")

        # — 2) build missing_gps.csv —
        found = set(gps_df["parcel_id"])
        missing = sorted(master_ids - found)
        missing_df = pd.DataFrame({"parcel_id": missing})
        missing_df.to_csv("data/missing_gps.csv", index=False)
        st.success("✅ missing_gps.csv written to data/")

        # — 3) build suppression status —
        # load each year into a set
        year_sets = {}
        for yf in year_files:
            df = pd.read_csv(yf, dtype=str)
            year = yf.name.split(".")[0].replace("Hawaii", "")
            year_sets[year] = set(df["parcel_id"].astype(str))

        rows = []
        latest = max(year_sets.keys(), key=lambda y: int(y))
        for pid in master_ids:
            present = [y for y,s in year_sets.items() if pid in s]
            if pid in year_sets[latest]:
                status = "Still Public"
            elif present:
                status = "Vanished After Use"
            else:
                status = "Fabricated / Never Listed"
            rows.append({"parcel_id": pid, "classification": status})

        sup_df = pd.DataFrame(rows)
        out = master_df.merge(sup_df, on="parcel_id", how="left")
        out.to_csv("data/Hawaii_tmk_suppression_status.csv", index=False)
        st.success("✅ Hawaii_tmk_suppression_status.csv written to data/")

        # allow quick download:
        st.download_button(
            "Download suppression status CSV",
            out.to_csv(index=False),
            file_name="Hawaii_tmk_suppression_status.csv",
            mime="text/csv"
        )
