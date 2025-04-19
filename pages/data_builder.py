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

    # 1) load all YAML docs from the ZIP
    with zipfile.ZipFile(yaml_zip) as zf:
        yaml_names = [n for n in zf.namelist() if n.lower().endswith((".yaml",".yml"))]
        docs = []
        for name in yaml_names:
            with zf.open(name) as f:
                docs.append(yaml.safe_load(f))

    # 2) load master TMKs
    master_df = pd.read_csv(master_csv, dtype=str)
    master_ids = set(master_df.iloc[:,0].astype(str))

    # 3) build year‑by‑year sets of TMKs
    year_sets = {}
    for yf in year_files:
        df = pd.read_csv(yf, dtype=str)
        # detect the right column name for parcel_id
        for cand in ("parcel_id","cty_tmk","TMK","TMK_txt"):
            if cand in df.columns:
                pid_col = cand
                break
        else:
            st.error(f"❌ {yf.name!r} has no parcel‑ID column (tried parcel_id, cty_tmk, TMK, TMK_txt)")
            continue

        # extract a 4‑digit year from the filename, or fallback
        m = re.search(r"(\d{4})", yf.name)
        year = m.group(1) if m else yf.name.rsplit(".",1)[0]
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

    # 5) mark fabricated: any YAML‑only IDs
    yaml_only = {
        str(tx.get("parcel_id"))
        for doc in docs
        for tx in doc.get("transactions", [])
        if tx.get("parcel_id") is not None
    } - master_ids

    sup_df.loc[sup_df["parcel_id"].isin(yaml_only), "classification"] = "Fabricated / Never Listed"

    # 6) extract GPS from YAMLs
    gps_rows = []
    for doc in docs:
        for tx in doc.get("transactions", []):
            pid = str(tx.get("parcel_id"))
            gps = tx.get("gps")
            if isinstance(gps, list) and len(gps) == 2:
                gps_rows.append({
                    "parcel_id": pid,
                    "latitude": gps[0],
                    "longitude": gps[1]
                })

    gps_df = pd.DataFrame(gps_rows).drop_duplicates()

    # 7) find which master TMKs are missing GPS
    missing = pd.DataFrame(
        [{"parcel_id": pid} for pid in master_ids if pid not in gps_df["parcel_id"].values]
    )

    # 8) provide download buttons
    st.success("✅ Done!")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.download_button(
            "📥 Download suppression CSV",
            sup_df.to_csv(index=False).encode("utf-8"),
            "Hawaii_tmk_suppression_status.csv",
            mime="text/csv"
        )
    with c2:
        st.download_button(
            "📥 Download GPS patch CSV",
            gps_df.to_csv(index=False).encode("utf-8"),
            "gps_patch.csv",
            mime="text/csv"
        )
    with c3:
        st.download_button(
            f"📥 Download missing GPS ({len(missing)})",
            missing.to_csv(index=False).encode("utf-8"),
            "missing_gps.csv",
            mime="text/csv"
        )

else:
    st.warning("Please upload all three inputs to build your data.")

