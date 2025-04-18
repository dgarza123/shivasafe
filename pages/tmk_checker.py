import os
import csv

PRIMARY_PATH = "data/Hawaii_tmk_master.csv"
FALLBACK_PATH = "data/Hawaii.csv"

def load_known_tmks():
    path = None
    if os.path.exists(PRIMARY_PATH):
        path = PRIMARY_PATH
    elif os.path.exists(FALLBACK_PATH):
        path = FALLBACK_PATH
    else:
        print(f"❌ TMK data not found. Expected one of:\n - {PRIMARY_PATH}\n - {FALLBACK_PATH}")
        return set()

    print(f"📄 Loaded TMK reference from: {path}")
    known_tmks = set()
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmk = row.get("parcel_id") or row.get("TMK") or row.get("tmk")
            if tmk:
                known_tmks.add(tmk.strip())
    return known_tmks

KNOWN_TMK_SET = load_known_tmks()

def get_parcel_status(parcel_id: str) -> str:
    if not parcel_id:
        return "Unknown"
    pid = parcel_id.strip()
    if pid in KNOWN_TMK_SET:
        return "Public"
    if len(pid) >= 5:
        return "Disappeared"
    return "Unknown"
