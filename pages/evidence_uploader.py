import os
import zipfile
import yaml
import streamlit as st
import importlib.util

# ————————————————————————————————————————————————
# Configuration
# ————————————————————————————————————————————————
EVIDENCE_DIR = "evidence"
DB_SCRIPT    = "scripts/rebuild_db_from_yaml.py"
DB_PATH      = "data/hawaii.db"

# ————————————————————————————————————————————————
# Page setup
# ————————————————————————————————————————————————
st.set_page_config(page_title="Admin: Upload & Validate YAMLs", layout="centered")
st.title("📂 Evidence Uploader & Validator")

st.markdown("""
Use this page to:
1. **Upload** a ZIP of your YAML documents.
2. **Extract** them into `/evidence/`.
3. **Validate** syntax and list how many valid YAMLs we have.
4. (Optional) **Rebuild** the SQLite DB from those YAMLs.
""")

# ————————————————————————————————————————————————
# 1) Ensure evidence folder exists
# ————————————————————————————————————————————————
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# ————————————————————————————————————————————————
# 2) Upload a ZIP of YAMLs
# ————————————————————————————————————————————————
uploaded_zip = st.file_uploader("📦 Upload .zip of YAMLs", type="zip")
if uploaded_zip:
    zip_path = os.path.join(EVIDENCE_DIR, uploaded_zip.name)
    # Save the ZIP
    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.read())
    st.success(f"✅ Uploaded to `{zip_path}`")
    # Extract it
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(EVIDENCE_DIR)
    st.info(f"📂 Extracted ZIP into `{EVIDENCE_DIR}/`")
    # Optionally flatten any nested folders
    for root, _, files in os.walk(EVIDENCE_DIR):
        for fname in files:
            if fname.lower().endswith((".yaml", ".yml")):
                src = os.path.join(root, fname)
                dst = os.path.join(EVIDENCE_DIR, fname)
                if src != dst:
                    os.replace(src, dst)
    st.info("🔄 Flattened YAMLs into one directory")

# ————————————————————————————————————————————————
# 3) List & validate YAML files
# ————————————————————————————————————————————————
existing = [
    f for f in os.listdir(EVIDENCE_DIR)
    if f.lower().endswith((".yaml", ".yml"))
]
st.markdown(f"### 🔍 Found **{len(existing)}** YAML file(s) in `{EVIDENCE_DIR}/`")
if existing:
    # Quick syntax check
    valid_count = 0
    for fname in existing:
        path = os.path.join(EVIDENCE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                yaml.safe_load(f)
            valid_count += 1
        except Exception as e:
            st.error(f"❌ Syntax error in `{fname}`: {e}")
    st.success(f"✅ {valid_count}/{len(existing)} YAMLs parsed without error")

# ————————————————————————————————————————————————
# 4) Optionally rebuild the DB
# ————————————————————————————————————————————————
st.markdown("---")
st.header("🔄 Rebuild SQLite Database")

if os.path.exists(DB_PATH):
    st.info(f"✅ Existing DB: `{DB_PATH}` ({os.path.getsize(DB_PATH):,} bytes)")
else:
    st.warning(f"❌ No DB found at `{DB_PATH}` — it will be created.")

if st.button("🚀 Rebuild `hawaii.db` Now"):
    # Remove old DB
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        st.write("🗑️ Removed old database")
    # Dynamically import & run the rebuild script
    if not os.path.exists(DB_SCRIPT):
        st.error(f"❌ Rebuild script not found at `{DB_SCRIPT}`")
    else:
        try:
            spec   = importlib.util.spec_from_file_location("rebuild", DB_SCRIPT)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            count = module.build_db()  # should return number of rows inserted
            st.success(f"🎉 Rebuild complete! Inserted **{count}** transactions.")
        except Exception as e:
            st.error(f"❌ Rebuild failed: {e}")
    # Confirm
    if os.path.exists(DB_PATH):
        st.info(f"📂 New DB is `{DB_PATH}` ({os.path.getsize(DB_PATH):,} bytes)")
    else:
        st.error("❌ Database still missing—check your rebuild script.")
