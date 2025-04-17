import os
import yaml
import sqlite3
import pandas as pd

def build_database_from_zip(folder: str, db_path: str) -> int:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)

    transactions = []
    for fname in os.listdir(folder):
        if fname.lower().endswith((".yaml", ".yml")):
            with open(os.path.join(folder, fname), "r") as f:
                ydata = yaml.safe_load(f)
                cert_id = ydata.get("certificate_number") or ydata.get("document") or fname
                for tx in ydata.get("transactions", []):
                    tx["certificate_id"] = cert_id
                    transactions.append(tx)

    df = pd.DataFrame(transactions)
    df = df[["certificate_id", "parcel_id", "grantor", "grantee", "amount", "escrow_id", "registry_key", "country", "link"]]

    coord_df = pd.read_csv("Hawaii.csv")
    merged_df = pd.merge(df, coord_df, on="parcel_id", how="left")
    merged_df["status"] = merged_df.apply(lambda x: "Public" if pd.notna(x.latitude) else "Private", axis=1)

    merged_df.to_sql("parcels", conn, index=False, if_exists="replace")
    conn.commit()
    conn.close()

    return len(merged_df)
