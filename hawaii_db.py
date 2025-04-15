import sqlite3
import os

DB_PATH = "Hawaii.db"

def get_coordinates_by_tmk(tmk: str):
    """
    Look up TMK in Hawaii.db and return (Latitude, Longitude) tuple.
    Returns None if TMK is not found or if database is missing.
    """
    if not os.path.exists(DB_PATH):
        print(f"[hawaii_db] Database not found: {DB_PATH}")
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Latitude, Longitude FROM tmk_lookup WHERE TMK = ?",
            (tmk.strip(),)
        )
        result = cursor.fetchone()
        conn.close()

        if result and all(result):
            return result[0], result[1]
    except Exception as e:
        print(f"[hawaii_db] Query failed: {e}")

    return None
