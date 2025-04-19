import os
import requests
import sqlite3
import streamlit as st

# ─────────────── CONFIG ───────────────
# Your Drive “share” file ID:
DRIVE_FILE_ID = "1QeV0lIlcaTUAp6O7OJGBtzagpQ_XJc1h"
# Where to save it locally:
DB_DIR      = "data"
DB_NAME     = "hawaii.db"
DB_PATH     = os.path.join(DB_DIR, DB_NAME)
# Direct‑download URL for Google Drive
DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={DRIVE_FILE_ID}"

# ─────────────── FETCH / CACHE ───────────────
def fetch_remote_db():
    os.makedirs(DB_DIR, exist_ok=True)
    with st.spinner("📥 Downloading remote database…"):
        r = requests.get(DOWNLOAD_URL, stream=True)
        r.raise_for_status()
        with open(DB_PATH, "wb") as f:
            for chunk in r.iter_content(8_192):
                f.write(chunk)

if not os.path.exists(DB_PATH):
    fetch_remote_db()

# ─────────────── CONNECT ───────────────
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur  = conn.cursor()

# ─────────────── STREAMLIT SETUP ───────────────
st.set_page_config(
    page_title="ShivaSafe",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────── NAVIGATION ───────────────
st.sidebar.title("🔎 Navigate")
page = st.sidebar.radio("", [
    "Map Viewer",
    "Heat Map",
    "Upload Evidence",
    "Admin"
])

# ─────────────── ROUTING ───────────────
if page == "Map Viewer":
    import pages.map_viewer as mv
    mv.show(cur)

elif page == "Heat Map":
    import pages.heat_map as hm
    hm.show(cur)

elif page == "Upload Evidence":
    import pages.evidence_uploader as eu
    eu.show(cur)

elif page == "Admin":
    import pages.admin_dashboard as ad
    ad.show(cur)
