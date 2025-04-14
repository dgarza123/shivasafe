import csv

def load_valid_tmks(filepath="data/valid_tmks.csv"):
    valid = set()
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tmk = row.get("TMK", "").strip()
                if tmk:
                    valid.add(tmk)
    except Exception as e:
        print(f"[TMK Loader] Failed to load TMKs: {e}")
    return valid

def validate_parcel_id(parcel_id, valid_tmk_set):
    if not parcel_id:
        return False
    return parcel_id.strip() in valid_tmk_set
