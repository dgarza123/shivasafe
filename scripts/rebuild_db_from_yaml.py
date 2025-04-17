import os
import yaml
import sqlite3
import hashlib

EVIDENCE_FOLDER = "evidence"
DB_PATH = "data/hawaii.db"

def sha256_of_file(file_path):
    if not os.path.isfile(file_path):
        return None
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def get_visibility_flags(block):
    return (
        1 if block.get("present_2015") else 0,
        1 if block.get("present_2018") else 0,
        1 if block.get("present_2022") else 0,
        1 if block.get("present_2025") else 0,
    )

def extract_transaction_blocks(data):
    for key in ["transactions", "payments", "entities"]:
        block = data.get(key)
        if isinstance(block, list) and all(isinstance(x, dict) for x in block):
            return block
    return []

def build_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS parcels")
    c.execute("""
        CREATE TABLE parcels (
            certificate_id TEXT,
            parcel_id TEXT,
            sha256 TEXT,
            grantee TEXT,
            amount TEXT,
            date TEXT,
            present_2015 INTEGER,
            present_2018 INTEGER,
            present_2022 INTEGER,
            present_2025 INTEGER
        )
    """)

    for fname in os.listdir(EVIDENCE_FOLDER):
        if not fname.endswith(".yaml"):
            continue

        try:
            with open(os.path.join(EVIDENCE_FOLDER, fname), "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                print(f"[!] Skipping {fname} — top-level YAML object is not a dictionary.")
                continue
        except Exception as e:
            print(f"[✘] Failed to parse {fname}: {e}")
            continue

        record_id = data.get("record_id") or fname.replace("_entities.yaml", "")
        pdf_file = data.get("pdf_file") or ""
        sha256 = data.get("sha256") or sha256_of_file(os.path.join(EVIDENCE_FOLDER, pdf_file))

        transactions = extract_transaction_blocks(data)
        if not transactions:
            print(f"[!] No valid transaction blocks found in {fname}. Skipped.")
            continue

        for txn in transactions:
            if not isinstance(txn, dict):
                print(f"[!] Skipped invalid transaction in {fname}: {txn}")
                continue

            parcel = txn.get("parcel") or txn.get("parcel_id")
            grantee = txn.get("grantee") or txn.get("recipient")
            amount = txn.get("amount") or txn.get("value")
            date = txn.get("date")

            vis_2015, vis_2018, vis_2022, vis_2025 = get_visibility_flags(txn)

            c.execute("""
                INSERT INTO parcels (
                    certificate_id, parcel_id, sha256, grantee, amount, date,
                    present_2015, present_2018, present_2022, present_2025
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id, parcel, sha256, grantee, amount, date,
                vis_2015, vis_2018, vis_2022, vis_2025
            ))

    conn.commit()
    conn.close()
    print("[✔] hawaii.db rebuilt successfully.")
