import sqlite3
import pandas as pd

# Load the CSV file
df = pd.read_csv("tmk_suppression_timeline.csv")

# Normalize values
for col in ["visible_2018", "visible_2022", "visible_2025"]:
    df[col] = df[col].map({True: 1, "True": 1, "✅": 1, False: 0, "False": 0, "❌": 0}).fillna(0).astype(int)

# Create SQLite database
conn = sqlite3.connect("Hawaii.db")
cursor = conn.cursor()

# Drop and create table
cursor.execute("DROP TABLE IF EXISTS tmk_suppression_timeline")
cursor.execute("""
CREATE TABLE tmk_suppression_timeline (
    TMK TEXT PRIMARY KEY,
    Certificate TEXT,
    visible_2018 INTEGER,
    visible_2022 INTEGER,
    visible_2025 INTEGER,
    status TEXT
)
""")

# Insert rows
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO tmk_suppression_timeline VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["TMK"],
        row["Certificate"],
        row["visible_2018"],
        row["visible_2022"],
        row["visible_2025"],
        row["status"]
    ))

conn.commit()
conn.close()

print("✅ Suppression timeline ingested into Hawaii.db")
