import sqlite3

DB_PATH = "Hawaii.db"

def get_coordinates_by_tmk(tmk: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT Latitude, Longitude FROM tmk_lookup WHERE TMK = ?", (tmk,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0], result[1]
    except Exception as e:
        print(f"[hawaii_db] DB error: {e}")
    return None