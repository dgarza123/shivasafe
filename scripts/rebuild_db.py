import os
import sqlite3
import yaml

def build_db(yaml_dir: str, output_path: str = "data/hawaii.db"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    conn = sqlite3.connect(output_path)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS parcels (
            certificate_id TEXT,
            parcel_id TEXT,
            parcel_valid BOOLEAN,
            grantor TEXT,
            grantee TEXT,
            amount TEXT,
            registry_key TEXT,
            escrow_id TEXT,
            transfer_bank TEXT,
            country TEXT,
            date_signed TEXT,
            link TEXT,
            status TEXT
        )
    """)

    count = 0
    yaml_files = [fname for fname in os.listdir(yaml_dir) if fname.endswith(".yaml")]
    
    if not yaml_files:
        raise Exception("No YAML files found in directory.")

    for fname in yaml_files:
        path = os.path.join(yaml_dir, fname)
        with open(path, "r") as f:
            data = yaml.safe_load(f)

            if not data or "transactions" not in data:
                continue  # Skip empty or invalid YAML files

            cert_id = os.path.splitext(fname)[0]

            for tx in data.get("transactions", []):
                row = (
                    cert_id,
                    tx.get("parcel_id"),
                    tx.get("parcel_valid", False),
                    tx.get("grantor"),
                    tx.get("grantee"),
                    tx.get("amount"),
                    tx.get("registry_key"),
                    tx.get("escrow_id"),
                    tx.get("transfer_bank"),
                    tx.get("country"),
                    tx.get("date_signed"),
                    tx.get("link"),
                    "Disappeared" if not tx.get("parcel_valid", False) else "Public"
                )
                c.execute("INSERT INTO parcels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
                count += 1

    conn.commit()
    conn.close()
    return count
