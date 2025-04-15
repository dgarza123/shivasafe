import pandas as pd
import sqlite3

df = pd.read_csv("Hawaii.csv")

conn = sqlite3.connect("Hawaii.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS tmk_lookup")
cursor.execute("""
CREATE TABLE tmk_lookup (
    TMK TEXT PRIMARY KEY,
    Latitude REAL,
    Longitude REAL
)
""")

for _, row in df.iterrows():
    cursor.execute("INSERT INTO tmk_lookup VALUES (?, ?, ?)", (
        str(row["TMK"]).strip(),
        float(row["Latitude"]),
        float(row["Longitude"])
    ))

conn.commit()
conn.close()

print("✅ Hawaii.db created successfully.")