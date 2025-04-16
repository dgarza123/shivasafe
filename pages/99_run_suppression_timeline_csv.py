import pandas as pd
import os

# === CONFIG ===
data_dir = "data"
out_path = os.path.join(data_dir, "tmk_suppression_timeline.csv")

# === Helper: Normalize GIS TMK format ===
def normalize_tmk(row):
    try:
        zone = str(int(row["zone"]))
        section = str(int(row["section"]))
        plat = str(int(row["plat"]))
        parcel = str(int(row["parcel"]))
        return f"{zone}-{section}-{plat}:{parcel}"
    except:
        return None

# === Load and normalize each year ===
def load_and_normalize(filename):
    path = os.path.join(data_dir, filename)
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df["tmk_normalized"] = df.apply(normalize_tmk, axis=1)
    return set(df["tmk_normalized"].dropna().str.strip())

# === Load all years ===
tmk_2018 = load_and_normalize("Hawaii2018.csv")
tmk_2022 = load_and_normalize("Hawaii2022.csv")
tmk_2025 = load_and_normalize("Hawaii2025.csv")

# === Load all YAML TMKs ===
yaml_dir = "evidence"
tmk_to_source = {}

for fname in os.listdir(yaml_dir):
    if not fname.endswith("_entities.yaml"):
        continue
    try:
        import yaml
        with open(os.path.join(yaml_dir, fname), "r") as f:
            ydata = yaml.safe_load(f)
        cert_id = os.path.splitext(fname)[0].replace("_entities", "")
        for tx in ydata.get("transactions", []):
            tmk = str(tx.get("parcel_id", "")).strip()
            if tmk:
                tmk_to_source[tmk] = {
                    "certificate": cert_id,
                    "yaml_file": fname
                }
    except:
        continue

# === Analyze suppression status ===
rows = []
for tmk, meta in tmk_to_source.items():
    found_2018 = tmk in tmk_2018
    found_2022 = tmk in tmk_2022
    found_2025 = tmk in tmk_2025

    if found_2018 and found_2022 and not found_2025:
        status = "Disappeared"
    elif not found_2018 and found_2022 and not found_2025:
        status = "Erased"
    elif not found_2018 and not found_2022 and not found_2025:
        status = "Fabricated"
    else:
        status = "Public"

    rows.append({
        "TMK": tmk,
        "certificate": meta["certificate"],
        "yaml_file": meta["yaml_file"],
        "found_2018": found_2018,
        "found_2022": found_2022,
        "found_2025": found_2025,
        "status": status
    })

# === Save to CSV ===
df_out = pd.DataFrame(rows)
df_out.to_csv(out_path, index=False)

print(f"✅ Suppression timeline saved to: {out_path}")
print(f"Rows written: {len(df_out)}")
