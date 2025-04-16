import streamlit as st
import zipfile
import os
import yaml
import sqlite3

st.set_page_config(page_title="Upload YAML Bundle", layout="centered")
st.title("📦 Upload & Ingest YAML Evidence")

UPLOAD_DIR = "evidence"
DB_PATH = "Hawaii.db"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_transactions_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            tmk TEXT,
            certificate TEXT,
            yaml_file TEXT
        )
    """)
    conn.commit()
    conn.close()

def ingest_yaml_to_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    count = 0
    for fname in os.listdir(UPLOAD_DIR):
        if not fname.endswith("_entities.yaml"):
            continue
        try:
            with open(os.path.join(UPLOAD_DIR, fname), "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            cert = fname.replace("_entities.yaml", "")
            for tx in data.get("transactions", []):
                tmk = str(tx.get("parcel_id", "")).strip()
                if not tmk:
                    continue
                c.execute("INSERT OR IGNORE INTO transactions (tmk, certificate, yaml_file) VALUES (?, ?, ?)",
                          (tmk, cert, fname))
                count += 1
        except Exception as e:
            st.warning(f"⚠️ Skipped {fname}: {e}")
            continue
    conn.commit()
    conn.close()
    return count

uploaded_file = st.file_uploader("Upload a ZIP file containing *_entities.yaml files", type="zip")

if uploaded_file:
    zip_path = os.path.join("temp.zip")
    with open(zip_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(UPLOAD_DIR)
        extracted = zip_ref.namelist()

    os.remove(zip_path)
    st.success(f"✅ Extracted {len(extracted)} files to /evidence")
    st.write(extracted)

    create_transactions_table()
    count = ingest_yaml_to_db()
    st.success(f"📥 Ingested {count} transactions into Hawaii.db")

    st.info("⬅️ Reload the suppression timeline to reflect new entries.")
