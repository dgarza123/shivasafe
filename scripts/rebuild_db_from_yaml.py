import os
import yaml
import sqlite3

DB_PATH = "data/hawaii.db"
TABLE_NAME = "parcels"
SOURCE_FOLDER = "evidence"

def create_table(conn):
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            certificate_id TEXT,
            sha256 TEXT,
            filename TEXT,
            grantor TEXT,
            grantee TEXT,
            amount TEXT,
            parcel_id TEXT,
            parcel_valid BOOLEAN,
            registry_key TEXT,
            escrow_id TEXT,
            transfer_bank TEXT,
            country TEXT,
            date_signed TEXT,
            status TEXT
        )
    """)
    conn.commit()

def parse_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def infer_status(entry):
    if not entry.get("parcel_valid", True):
        return "Disappeared"
    return "Public"

def normalize_top_level(data, path):
    return {
        "cert": data.get("certificate_number") or data.get("cert_id") or os.path.splitext(os.path.basename(path))[0],
        "sha": data.get("sha256", ""),
        "filename": data.get("document") or data.get("file_name") or ""
    }

def normalize_parcel_id(raw_parcel):
    if not raw_parcel:
        return ""
    if isinstance(raw_parcel, str) and "TMK" in raw_parcel:
        raw_parcel = raw_parcel.replace("TMK:", "").replace("TMK", "").strip()
    return raw_parcel.strip()

def normalize_transaction(tx):
    raw_parcel = tx.get("parcel_id") or tx.get("parcel") or ""
    return {
        "grantor": tx.get("grantor"),
        "grantee": tx.get("grantee"),
        "amount": tx.get("amount") or tx.get("amount_usd"),
        "parcel_id": normalize_parcel_id(raw_parcel),
        "parcel_valid": bool(tx.get("parcel_valid", True)),
        "registry_key": tx.get("registry_key"),
        "escrow_id": tx.get("escrow_id"),
        "transfer_bank": tx.get("transfer_bank"),
        "country": tx.get("country"),
        "date_signed": tx.get("date_signed") or tx.get("signing_date") or "",
        "status": infer_status(tx)
    }

def build_db():
    if not os.path.exists(SOURCE_FOLDER):
        raise FileNotFoundError(f"Missing folder: {SOURCE_FOLDER}")

    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    create_table(conn)

    inserted = 0
    yaml_paths = []
    for root, _, files in os.walk(SOURCE_FOLDER):
        for file in files:
            if file.lower().endswith(".yaml"):
                yaml_paths.append(os.path.join(root, file))

    print(f"\n📁 Scanning {len(yaml_paths)} YAML file(s) in {SOURCE_FOLDER}\n")

    for path in yaml_paths:
        try:
            data = parse_yaml(path)
            if not data:
                print(f"❌ {path} — EMPTY or not parseable")
                continue

            if "transactions" not in data or not isinstance(data["transactions"], list):
                print(f"❌ {path} — MISSING or invalid 'transactions' list")
                continue

            header = normalize_top_level(data, path)
            txs = data["transactions"]

            print(f"\n📄 Processing: {os.path.basename(path)} ({len(txs)} transactions)")

            for i, tx in enumerate(txs):
                tx_norm = normalize_transaction(tx)
                print(f"\n  🔍 TX {i+1} normalized:\n    " + "\n    ".join(f"{k}: {repr(v)}" for k, v in tx_norm.items()))

                # Skip logic with reason logging
                if not tx_norm["grantor"] or not tx_norm["grantee"]:
                    print(f"  ⚠️ Skipped TX {i+1}: Missing grantor or grantee")
                    continue

                if not tx_norm["parcel_id"]:
                    print(f"  ⚠️ Skipped TX {i+1}: Missing or invalid parcel_id")
                    continue

                try:
                    conn.execute(f"""
                        INSERT INTO {TABLE_NAME} (
                            certificate_id, sha256, filename, grantor, grantee,
                            amount, parcel_id, parcel_valid, registry_key,
                            escrow_id, transfer_bank, country, date_signed, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        header["cert"],
                        header["sha"],
                        header["filename"],
                        tx_norm["grantor"],
                        tx_norm["grantee"],
                        tx_norm["amount"],
                        tx_norm["parcel_id"],
                        tx_norm["parcel_valid"],
                        tx_norm["registry_key"],
                        tx_norm["escrow_id"],
                        tx_norm["transfer_bank"],
                        tx_norm["country"],
                        tx_norm["date_signed"],
                        tx_norm["status"]
                    ))
                    inserted += 1
                    print(f"  ✅ Inserted TX {i+1}")
                except Exception as e:
                    print(f"  ❌ DB error TX {i+1}: {e}")

        except Exception as e:
            print(f"❌ Failed to parse {path}: {e}")

    conn.commit()
    conn.close()
    print(f"\n✅ Done. Inserted {inserted} transaction(s).\n")
    return inserted
