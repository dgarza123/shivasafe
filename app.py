# app.py
import os
import sys

# ensure our root folder is on the import path
BASE_DIR = os.path.dirname(__file__)
sys.path.insert(0, BASE_DIR)

import streamlit as st
from database_builder import build_database_from_zip

# paths
DB_PATH  = os.path.join("data", "hawaii.db")
ZIP_PATH = os.path.join("data", "hawaii_bundle.zip")  # put your zip here

# on first run, build DB if missing
if not os.path.exists(DB_PATH):
    st.info("Building local SQLite database…")
    build_database_from_zip(ZIP_PATH, DB_PATH)
    st.success("Database ready!")

# now connect and use DB…
import sqlite3
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
# … the rest of your Streamlit UI goes here …
st.write("🎉 Your app is up and running with a fresh database!")
