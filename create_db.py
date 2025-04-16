# STEP 1: Write this file as create_db.py
import os, sqlite3, base64

DB_PATH = "data/hawaii.db"

# Full base64-encoded SQLite database (generated from your YAMLs, cleaned and normalized)
BASE64_DB = """
<PASTE_FULL_BASE64_BLOB_HERE>
"""

def write_db():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "wb") as f:
            f.write(base64.b64decode(BASE64_DB.strip()))
        print("hawaii.db created.")
    else:
        print("hawaii.db already exists.")

if __name__ == "__main__":
    write_db()
