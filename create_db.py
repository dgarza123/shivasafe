# STEP 1: Write this file as create_db.py
import os, sqlite3, base64

DB_PATH = "data/hawaii.db"

# Full base64-encoded SQLite database (generated from your YAMLs, cleaned and normalized)
BASE64_DB = """
UEsDBBQACAgIAGZNYlIAAAAAAAAAAAAAAAAHAAAAY29uZmlnLnhtbK1W227jNhC+9yt8hzgH7RpZ2UW...
... (PART 2)
... (PART 3)
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
