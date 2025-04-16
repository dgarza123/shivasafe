import streamlit as st
import os
from create_db import write_db  # <- NEW LINE to trigger hawaii.db setup
from login_manager import is_logged_in, current_user, current_role, logout

# === Auto-create DB on startup ===
write_db()

st.set_page_config(page_title="Shiva PDF Analyzer", layout="wide")

# === Top Banner ===
st.markdown("""
# Shiva PDF Analyzer  
### Fast Facts: Hawaii Land Title Suppression

- **100%** of Torrens Certificates on the Hawaii Bureau of Conveyances server contain encoded transaction data that does not match the visible, rendered text.  
- Hidden records reveal private sales of government land, with funds routed to the **Science of Identity Foundation**, the **Gabbard Trust**, and individuals including **Tulsi Gabbard** and **Mike Gabbard**.  
- Proceeds are consistently directed to **banks in the Philippines**.  
- Since **2018**, nearly **1,500 land parcels** have quietly disappeared from public DLNR records — with **no audit trail** or notification to the public.  
- During most of this period, **Mike Gabbard chaired the DLNR oversight committee**.  
- This site was created to document these abnormalities and shed light on what may be a **$3 billion theft of Hawaii government land**.
""")

# === Sidebar Navigation ===
st.sidebar.title("📁 Navigation")
st.sidebar.markdown("- [Homepage](app)")
st.sidebar.markdown("- [Map Viewer](map_viewer)")
st.sidebar.markdown("- [Timeline](timeline)")
st.sidebar.markdown("- [Suppression Map](suppression_heatmap)")
st.sidebar.markdown("- [Suppression Timeline](suppression_timeline)")

# === Admin Tools Only for Logged-In Editors/Admins ===
if is_logged_in() and current_role() in ["admin", "editor"]:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔐 Admin Tools")
    st.sidebar.markdown("- [Admin Dashboard](admin_home)")
    st.sidebar.markdown("- [Login Manager](login)")
    st.sidebar.markdown("- [Upload to Drive](upload_to_drive)")

# === User Login Status ===
st.sidebar.markdown("---")
if is_logged_in():
    st.sidebar.success(f"Logged in as: **{current_user()}**")
    if st.sidebar.button("Log Out"):
        logout()
        st.experimental_rerun()
else:
    st.sidebar.info("You are not logged in.")
