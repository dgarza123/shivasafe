import pandas as pd
import sqlite3
import os

# === Load CSV from scripts folder ===
csv_path = os.path.join("scripts", "tmk_suppression_timeline.csv")
df = pd.read_csv(csv_path)

# === Normalize visibility columns ===
for col in ["visible_2018", "visible_2022", "visible_2025"]:
    df[col] = df[col].map({"✅": 1, "❌": 0, True: 1, False: 0}).fillna(0).astype(int)

# === Create or update SQLite database ===
conn = sqlite3.connect("Hawaii.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS tmk_suppression_timeline")
cursor.execute("""
CREATE TABLE tmk_suppression_timeline (
    TMK TEXT PRIMARY KEY,
    certificate TEXT,
    yaml_file TEXT,
    visible_2018 INTEGER,
    visible_2022 INTEGER,
    visible_2025 INTEGER,
    status TEXT
)
""")

# === Insert rows ===
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO tmk_suppression_timeline VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        row["TMK"],
        row["certificate"],
        row["yaml_file"],
        row["visible_2018"],
        row["visible_2022"],
        row["visible_2025"],
        row["status"]
    ))

conn.commit()
conn.close()

print("✅ Suppression timeline successfully loaded into Hawaii.db")
