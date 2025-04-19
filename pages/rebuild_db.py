# pages/rebuild_db.py

import io
import os
import tempfile

import streamlit as st
from database_builder import build_database_from_zip

st.set_page_config(page_title="🔄 Rebuild SQLite Database", layout="centered")
st.title("🔄 Rebuild SQLite Database")

st.markdown(
    """
    Upload a ZIP containing:
      - `evidence/*.yaml`
      - `data/*.csv`
    
    This will rebuild `data/hawaii.db` in one click.
    """
)

# 1) Upload ZIP
uploaded = st.file_uploader("📦 Upload your ZIP of YAMLs + CSVs", type="zip", help="Should contain both your `evidence/` and `data/` files.", key="zip")
out_db = st.text_input("📁 Output DB path", value="data/hawaii.db", help="Where to write the rebuilt database")

if uploaded and st.button("Rebuild now"):
    # write upload to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp.write(uploaded.getbuffer())
        tmp_path = tmp.name

    # ensure parent directory exists
    os.makedirs(os.path.dirname(out_db), exist_ok=True)

    with st.spinner("🔨 Building database..."):
        try:
            # your function signature: build_database_from_zip(zip_path, out_db)
            build_database_from_zip(tmp_path, out_db)
            st.success(f"✅ New DB created at `{out_db}`")
        except Exception as e:
            st.error(f"❌ Rebuild failed: {e}")
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
