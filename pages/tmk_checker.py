import csv

KNOWN_TMK_PATH = "data/Hawaii_tmk_master.csv"  # Replace if needed

def load_known_tmks():
    known = set()
    with open(KNOWN_TMK_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmk = row.get("parcel_id") or row.get("TMK") or row.get("tmk")
            if tmk:
                known.add(tmk.strip())
    return known

KNOWN_TMK_SET = load_known_tmks()

def get_parcel_status(parcel_id):
    if not parcel_id:
        return "Unknown"
    parcel_id = parcel_id.strip()
    if parcel_id in KNOWN_TMK_SET:
        return "Public"
    if any(parcel_id[:len(t)] == t for t in KNOWN_TMK_SET):
        return "Disappeared"
    return "Fabricated"
