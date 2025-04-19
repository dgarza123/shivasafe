import os
import sqlite3
import pandas as pd
import streamlit as st
import gdown

# — Google Drive file IDs —
DB_ID   = "1QeV0lIlcaTUAp6O7OJGBtzagpQ_XJc1h"
SUP_ID  = "1_Q3pT2sNF3nfCUzWyzBQF5u7lcy-q122"

# — construct direct‑download URLs —
DB_URL  = f"https://drive.google.com/uc?export=download&id={DB_ID}"
SUP_URL = f"https://drive.google.com/uc?export=download&id={SUP_ID}"

# — local cache paths —
os.makedirs("data", exist_ok=True)
DB_LOCAL  = "data/hawaii.db"
SUP_LOCAL = "data/suppression_status.csv"

@st.cache_resource
def get_connection():
    if not os.path.exists(DB_LOCAL):
        gdown.download(DB_URL, DB_LOCAL, quiet=False)
    # open read‑only
    return sqlite3.connect(f"file:{DB_LOCAL}?mode=ro", uri=True)

@st.cache_data
def load_suppression_csv():
    if not os.path.exists(SUP_LOCAL):
        gdown.download(SUP_URL, SUP_LOCAL, quiet=False)
    return pd.read_csv(SUP_LOCAL, dtype=str)

# ---- in your main Streamlit script ----

# 1) grab your DB
conn = get_connection()
cur  = conn.cursor()

# 2) grab your suppression table
sup_df = load_suppression_csv()

# 3) (optional) write it into your DB connection so queries can join on it
sup_df.to_sql("suppression_status", conn, if_exists="replace", index=False)

# 4) hand off to your map viewer
import map_viewer as mv
mv.show(cur)
