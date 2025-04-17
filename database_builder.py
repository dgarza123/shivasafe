import os
import yaml
import sqlite3
import zipfile
import streamlit as st
from datetime import datetime

DB_PATH = "data/hawaii.db"
UPLOAD_DIR = "uploads/extracted"

def extract_zip(zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(UPLOAD_DIR)
    return UPLOAD_DIR

def infer_status(yaml_tx):
    if yaml_tx.get("parcel_valid") is True:
        return "Public"
    if yaml_tx.get("parcel_valid") is False:
        return "Disappeared"
    if str(yaml_tx.get("parcel_id")).lower() in ["n/a", "unknown"]:
        return "Unknown"
    return "Unknown"

def create_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS parcels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT,
            parcel_id TEXT,
            grantee TEXT,
            grantor TEXT,
            amount TEXT,
            country TEXT,
            transfer_bank TEXT,
            registry_key TEXT,
            escrow_id TEXT,
            date_signed TEXT,
            status TEXT,
            sha256 TEXT,
            source_file TEXT
        )
    """)
    conn.commit()

def insert_transaction(conn, tx, cert_id, sha256, source_file):
    fields = [
        cert_id,
        tx.get("parcel_id"),
        tx.get("grantee"),
        tx.get("grantor"),
        tx.get("amount"),
        tx.get("country"),
        tx.get("transfer_bank"),
        tx.get("registry_key"),
        tx.get("escrow_id"),
        tx.get("date_signed"),
        infer_status(tx),
        sha256,
        source_file
    ]
    conn.execute("""
        INSERT INTO parcels (
            certificate_id, parcel_id, grantee, grantor, amount,
            country, transfer_bank, registry_key, escrow_id,
            date_signed, status, sha256, source_file
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, fields)

def build_database_from_folder(folder):
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    total = 0
    for fname in os.listdir(folder):
        if not fname.endswith(".yaml"):
            continue
        try:
            path = os.path.join(folder, fname)
            with open(path, "r") as f:
                data = yaml.safe_load(f)

            sha256 = data.get("sha256") or ""
            source_file = data.get("document") or ""
            cert_id = data.get("certificate") or os.path.splitext(fname)[0]
            for tx in data.get("transactions", []):
                insert_transaction(conn, tx, cert_id, sha256, source_file)
                total += 1
        except Exception as e:
            st.warning(f"⚠️ Failed to process {fname}: {e}")

    conn.commit()
    conn.close()
    return total, DB_PATH

def reset_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        st.info("\n\n⛔ Removed existing hawaii.db")
