import os
import pandas as pd
import yaml

# === Load TMK Registries ===
df_2018 = pd.read_csv("data/Hawaii2018.csv")
df_2022 = pd.read_csv("data/Hawaii2022.csv")
df_2025 = pd.read_csv("data/Hawaii2025.csv")

tmks_2018 = set(df_2018["TMK"].astype(str).str.strip())
tmks_2022 = set(df_2022["TMK"].astype(str).str.strip())
tmks_2025 = set(df_2025["TMK"].astype(str).str.strip())

# === Load YAML Evidence Files ===
EVIDENCE_DIR = "evidence"
rows = []

for fname in os.listdir(EVIDENCE_DIR):
    if not fname.endswith("_entities.yaml"):
        continue

    path = os.path.join(EVIDENCE_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    cert = fname.replace("_entities.yaml", "").replace("Certificate", "").strip()
    sha = data.get("sha256", "")
    pdf = data.get("document", "")
    transactions = data.get("transactions", [])

    for tx in transactions:
        tmk = str(tx.get("parcel_id", "")).strip()
        if not tmk:
            continue

        found_2018 = tmk in tmks_2018
        found_2022 = tmk in tmks_2022
        found_2025 = tmk in tmks_2025

        # === Classify Suppression Status ===
        if not found_2018 and not found_2022 and not found_2025:
            status = "Fabricated"
        elif found_2022 and not found_2018 and not found_2025:
            status = "Erased"
        elif (found_2018 or found_2022) and not found_2025:
            status = "Disappeared"
        elif found_2025:
            status = "Public"
        else:
            status = "Unknown"

        rows.append({
            "TMK": tmk,
            "certificate": cert,
            "yaml": fname,
            "found_2018": "✅" if found_2018 else "❌",
            "found_2022": "✅" if found_2022 else "❌",
            "found_2025": "✅" if found_2025 else "❌",
            "status": status,
            "sha256": sha,
            "document": pdf
        })

# === Save Timeline CSV ===
output_path = "data/tmk_suppression_timeline.csv"
os.makedirs("data", exist_ok=True)
pd.DataFrame(rows).to_csv(output_path, index=False)
print(f"✅ Suppression timeline saved to {output_path}")
