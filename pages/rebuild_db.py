# File: pages/rebuild_db.py

import streamlit as st
import os
import importlib.util

st.set_page_config(page_title="Rebuild Database", layout="centered")
st.title("🔧 Rebuild Hawaii DB from YAML Evidence")

DB_PATH     = "data/hawaii.db"
SCRIPT_PATH = "scripts/rebuild_db_from_yaml.py"  # ← updated to look in scripts/

st.markdown("""
Use this page to **(re)build** your `hawaii.db` from all YAMLs in `/evidence/`.
""")

# Show current status
if os.path.exists(DB_PATH):
    size = os.path.getsize(DB_PATH)
    st.info(f"✅ Found existing database (`data/hawaii.db`), size: {size:,} bytes.")
else:
    st.warning("❌ No existing `data/hawaii.db` found. It will be created.")

# Button to trigger rebuild
if st.button("🚀 Rebuild `data/hawaii.db` Now"):
    # 1️⃣ Delete old DB if present
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        st.write("🗑️ Deleted old `hawaii.db`.")

    # 2️⃣ Import and run your rebuild script
    if not os.path.exists(SCRIPT_PATH):
        st.error(f"❌ Rebuild script not found at `{SCRIPT_PATH}`. Please verify its location.")
    else:
        try:
            spec   = importlib.util.spec_from_file_location("rebuild", SCRIPT_PATH)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            count = module.build_db()  # returns number of inserted rows
            st.success(f"🎉 Rebuild complete! Inserted **{count}** transactions into `hawaii.db`.")
        except Exception as e:
            st.error(f"❌ Rebuild failed: {e}")

    # 3️⃣ Confirm new DB exists
    if os.path.exists(DB_PATH):
        new_size = os.path.getsize(DB_PATH)
        st.info(f"📂 `data/hawaii.db` now exists, size: {new_size:,} bytes.")
    else:
        st.error("❌ Still no `hawaii.db` found—please check your rebuild script.")
