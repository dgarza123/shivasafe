# File: pages/rebuild_db.py

import streamlit as st
import os
import importlib.util

st.set_page_config(page_title="Rebuild Database", layout="centered")
st.title("🔧 Rebuild Hawaii DB from YAML Evidence")

DB_PATH = "data/hawaii.db"
SCRIPT_PATH = "rebuild_db_from_yaml.py"  # adjust if you put it under scripts/

st.markdown("""
Use this page to **(re)build** your `hawaii.db` from all YAMLs in `/evidence`.
""")

# Show current status
if os.path.exists(DB_PATH):
    st.info(f"✅ Current database found with size {os.path.getsize(DB_PATH)} bytes.")
else:
    st.warning("❌ No existing `data/hawaii.db` found. It will be created.")

if st.button("🚀 Rebuild `data/hawaii.db` Now"):
    # 1) Delete old DB
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        st.write("🗑️ Deleted existing `hawaii.db`.")

    # 2) Dynamically import and run rebuild script
    try:
        spec = importlib.util.spec_from_file_location("rebuild", SCRIPT_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        count = module.build_db()  # should return inserted count
        st.success(f"🎉 Rebuild complete! Inserted **{count}** transactions into `hawaii.db`.")
    except Exception as e:
        st.error(f"❌ Rebuild failed: {e}")

    # 3) Confirm file now exists
    if os.path.exists(DB_PATH):
        st.info(f"📂 `data/hawaii.db` is now {os.path.getsize(DB_PATH)} bytes.")
    else:
        st.error("❌ Still no database found—please check your rebuild script.")
