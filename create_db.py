import os
import base64

DB_PATH = "data/hawaii.db"

DB_B64 = """
<PASTE FULL BASE64 BLOCK FROM NEXT MESSAGE HERE>
""".strip()

def write_db_if_missing():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with open(DB_PATH, "wb") as f:
            f.write(base64.b64decode(DB_B64))
        print(f"[✓] hawaii.db written to {DB_PATH}")
    else:
        print(f"[✓] hawaii.db already exists at {DB_PATH}")
