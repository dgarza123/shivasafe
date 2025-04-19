# pages/data_builder.py

import streamlit as st
import pandas as pd
import yaml
import zipfile
import io
import re

st.set_page_config(page_title="Data Builder", layout="wide")
st.title("🛠️ Data Builder")

st.markdown("""
Upload your evidence YAMLs (as a ZIP), the master TMK CSV, and your historical year CSVs below.  
Then hit **Download** to get your suppression status and GPS patches.
""")

yaml_zip = st.file_uploader("1) Upload evidence YAMLs (ZIP)", type="zip")
master_csv = st.file_uploader("2) Upload master TMK CSV", type="csv")
year_files = st.file_uploader(
    "3) Upload historical year CSVs (e.g. Hawaii2020.csv, Hawaii2021.csv…)",
    type="csv", accept_multiple_files=True
)

if yaml_zip and master_csv and year_files:
    st.info("⏳ Processing…")

    # 1) load all YAML docs from the ZIP, using safe_load_all and only keep dicts
    docs = []
    with zipfile.ZipFile(yaml_zip) as zf:
        yaml_names = [n for n in zf.namelist() if n.lower().endswith((".yaml", ".yml"))]
        for name in yaml_names:
            with zf.open(name) as f:
                text = f.read().decode("utf-8")
                for obj in yaml.safe_load_all(text):
                    if isinstance(obj, dict):
                        docs.append(obj)

    # 2) load master TMKs
    master_df = pd.read_csv(master_csv, dtype=str)
    master_ids = set(master_df.iloc[:, 0].astype(str))

    # 3) build year‑by‑year sets of TMKs
    year_sets = {}
    for yf in year_files:
        df = pd.read_csv(yf, dtype=str)
        # auto‑detect parcel_id column
        for cand in ("parcel_id", "cty_tmk", "TMK", "TMK_txt"):
            if cand in df.columns:
                pid_col = cand
                break
        else:
            st.error(f"❌ {yf.name!r} missing parcel‑ID column (tried {cand})")
            continue

        # extract year from filename
        m = re.search(r"(\d{4})", yf.name)
        year = m.group(1) if m else yf.name.rsplit(".", 1)[0]
        year_sets[year] = set(df[pid_col].astype(str))

    if not year_sets:
        st.error("No valid year files ingested.")
        st.stop()

    latest = max(year_sets.keys(), key=lambda y: int(y))

    # 4) classify each master TMK
    rows = []
    for pid in sorted(master_ids):
        in_latest = pid in year_sets[latest]
        ever = any(pid in s for s in year_sets.values())
        if in_latest and ever:
            cls = "Still Public"
        elif ever and not in_latest:
            cls = "Suppressed After Use"
        else:
            cls = "Vanished After Use"
        rows.append({"parcel_id": pid, "classification": cls})
    sup_df = pd.DataFrame(rows)

    # 5) mark fabricated (YAML‑only) parcels
    yaml_ids = {
        str(tx.get("parcel_id"))
        for doc in docs
        for tx in (doc.get("transactions") or [])
        if isinstance(tx, dict) and tx.get("parcel_id") is not None
    }
    fabricated = yaml_ids - master_ids
    sup_df.loc[sup_df["parcel_id"].isin(fabricated), "classification"] = "Fabricated / Never Listed"

    # 6) extract GPS from YAMLs
    gps_rows = []
    for doc in docs:
        for tx in (doc.get("transactions") or []):
            if not isinstance(tx, dict):
                continue
            pid = str(tx.get("parcel_id"))
            gps = tx.get("gps")
            if isinstance(gps, list) and len(gps) == 2:
                gps_rows.append({
                    "parcel_id": pid,
                    "latitude": gps[0],
                    "longitude": gps[1]
                })
    gps_df = pd.DataFrame(gps_rows).drop_duplicates()

    # 7) find master TMKs missing GPS
    missing = pd.DataFrame(
        [{"parcel_id": pid} for pid in master_ids if pid not in gps_df["parcel_id"].values]
    )

    # 8) download buttons
    st.success("✅ Done!")
    c1, c2, c3 = st.columns(3)
    c1.download_button(
        "📥 Download suppression CSV",
        sup_df.to_csv(index=False).encode("utf-8"),
        "Hawaii_tmk_suppression_status.csv",
        mime="text/csv",
    )
    c2.download_button(
        "📥 Download GPS patch CSV",
        gps_df.to_csv(index=False).encode("utf-8"),
        "gps_patch.csv",
        mime="text/csv",
    )
    c3.download_button(
        f"📥 Download missing GPS ({len(missing)})",
        missing.to_csv(index=False).encode("utf-8"),
        "missing_gps.csv",
        mime="text/csv",
    )

else:
    st.warning("Please upload all three inputs to build your data.")
