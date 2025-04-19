# pages/data_builder.py
import streamlit as st
import pandas as pd
import yaml, zipfile, io, os

st.set_page_config(page_title="🔨 Data Builder", layout="wide")
st.title("🔨 Data Builder")

st.markdown("""
Upload your **YAML ZIP**, your **Hawaii_tmk_master.csv**, and your **year CSVs** (e.g. Hawaii2020.csv, …).  
Click **Build all CSVs** to produce:

- `data/gps_patch.csv`  
- `data/missing_gps.csv`  
- `data/Hawaii_tmk_suppression_status.csv`  
""")

yaml_zip = st.file_uploader("1️⃣ Upload YAML ZIP", type="zip")
master_csv = st.file_uploader("2️⃣ Upload Hawaii_tmk_master.csv", type="csv")
year_files = st.file_uploader(
    "3️⃣ Upload historical year CSVs", 
    type="csv", accept_multiple_files=True
)

if yaml_zip and master_csv and year_files:
    if st.button("▶️ Build all CSVs"):
        # ensure data/ exists
        os.makedirs("data", exist_ok=True)

        # load master TMK table
        master_df = pd.read_csv(master_csv, dtype=str)
        master_df["parcel_id"] = master_df["parcel_id"].astype(str)
        master_ids = set(master_df["parcel_id"])

        # — 1) extract all GPS from the YAML ZIP —
        gps_recs = []
        z = zipfile.ZipFile(io.BytesIO(yaml_zip.read()))
        for fn in z.namelist():
            if fn.lower().endswith((".yaml", ".yml")):
                raw = z.read(fn)
                try:
                    loaded = yaml.safe_load(raw)
                except Exception as e:
                    st.warning(f"⚠️ Skipping {fn}: YAML parse error")
                    continue

                # normalize to list of docs
                docs = loaded if isinstance(loaded, list) else [loaded]
                for doc in docs:
                    if not isinstance(doc, dict):
                        continue
                    for tx in doc.get("transactions", []):
                        pid = tx.get("parcel_id")
                        gps = tx.get("gps")
                        if pid and gps and isinstance(gps, (list, tuple)) and len(gps) == 2:
                            # normalize parcel_id (strip punctuation)
                            pid_str = str(pid).replace(":", "").replace("-", "")
                            gps_recs.append({
                                "parcel_id": pid_str,
                                "latitude": gps[0],
                                "longitude": gps[1]
                            })

        gps_df = (
            pd.DataFrame(gps_recs)
              .drop_duplicates("parcel_id")
        )
        gps_df.to_csv("data/gps_patch.csv", index=False)
        st.success("✅ gps_patch.csv written to data/")

        # — 2) build missing_gps.csv —
        found = set(gps_df["parcel_id"])
        missing = sorted(master_ids - found)
        missing_df = pd.DataFrame({"parcel_id": missing})
        missing_df.to_csv("data/missing_gps.csv", index=False)
        st.success("✅ missing_gps.csv written to data/")

        # — 3) build suppression status —
        year_sets = {}
        for yf in year_files:
            df = pd.read_csv(yf, dtype=str)
            year = yf.name.replace(".csv", "").replace("Hawaii", "")
            year_sets[year] = set(df["parcel_id"].astype(str))

        latest = max(year_sets.keys(), key=lambda y: int(y))
        rows = []
        for pid in master_ids:
            if pid in year_sets[latest]:
                status = "Still Public"
            else:
                # disappeared if in any earlier year
                appeared = any(pid in s for y,s in year_sets.items() if y != latest)
                status = "Vanished After Use" if appeared else "Fabricated / Never Listed"
            rows.append({"parcel_id": pid, "classification": status})

        sup_df = pd.DataFrame(rows)
        out = master_df.merge(sup_df, on="parcel_id", how="left")
        out.to_csv("data/Hawaii_tmk_suppression_status.csv", index=False)
        st.success("✅ Hawaii_tmk_suppression_status.csv written to data/")

        # download button for the suppression CSV
        csv_bytes = out.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download suppression status CSV",
            csv_bytes,
            file_name="Hawaii_tmk_suppression_status.csv",
            mime="text/csv"
        )
