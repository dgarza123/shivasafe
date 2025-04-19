#!/usr/bin/env python3
# app.py — entry point for Streamlit

import os
import sys

# ─── 1) FORCE‑ADD YOUR ROOT & SUBDIRS TO PYTHONPATH ────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add repo root
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Add any subfolders you import from
SUBDIRS = ["pages", "scripts", "upload"]
for sub in SUBDIRS:
    p = os.path.join(BASE_DIR, sub)
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)


# ─── 2) IMPORT STREAMLIT & YOUR PAGES ─────────────────────────────────────────────
import streamlit as st

# ─── 3) UI & NAVIGATION ───────────────────────────────────────────────────────────
st.set_page_config(page_title="ShivaSafe", layout="wide")
st.sidebar.title("🔹 ShivaSafe")
page = st.sidebar.selectbox("Go to", [
    "Suppression Heatmap",
    "TMK Checker",
])

if page == "Suppression Heatmap":
    import pages.map_viewer as mv
    mv.run()
elif page == "TMK Checker":
    import pages.tmk_checker as tc
    tc.run()
