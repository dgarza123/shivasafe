# File: scripts/tmk_checker.py

import os
import csv

# Try these paths in order until one exists:
CANDIDATE_PATHS = [
    "data/Hawaii_tmk_master.csv",
    "data/Hawaii.csv",
    "/mnt/data/Hawaii_tmk_master.csv",
    "/mnt/data/Hawaii.csv",
]

def load_known_tmks():
    path = None
    for p in CANDIDATE_PATHS:
        if os.path.exists(p):
            path = p
            break

    if not path:
        print("❌ TMK reference not found. Looked for:")
        for p in CANDIDATE_PATHS:
            print("   -", p)
        return set()

    print(f"📄 Loaded TMK reference from: {path}")
    known = set()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Try the common column names
            tmk = row.get("parcel_id") or row.get("TMK") or row.get("tmk")
            if tmk:
                known.add(str(tmk).strip())
    return known

# Build once at import
KNOWN_TMK_SET = load_known_tmks()

def get_parcel_status(parcel_id: str) -> str:
    """
    Classify a parcel_id into:
      - 'Public' if it's in the known set
      - 'Disappeared' if it's well-formed (length >=5) but not found
      - 'Fabricated' otherwise
    """
    if not parcel_id:
        return "Fabricated"
    pid = str(parcel_id).strip()
    if pid in KNOWN_TMK_SET:
        return "Public"
    # if it looks like a valid TMK but not in set
    if len(pid) >= 5:
        return "Disappeared"
    # fallback for everything else
    return "Fabricated"
