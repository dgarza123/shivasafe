import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Suppression Loader", layout="centered")
st.title("📥 Load Suppression Timeline into Hawaii.db")

try:
    # === Paths ===
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "..", "scripts", "tmk_suppression_timeline.csv")
    db_path = os.path.join(script_dir, "..", "Hawaii.db")

    # === Load CSV ===
    df = pd.read_csv(csv_path)

    # === Normalize ✅/❌ → 1/0 ===
    for col in ["visible_2018", "visible_2022", "visible_2025"]:
        df[col] = df[col].map({"✅": 1, "❌": 0, True: 1, False: 0}).fillna(0).astype(int)

    # === Connect to DB ===
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # === Reset Table ===
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

    # === Insert Data ===
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

    st.success("✅ Suppression timeline successfully loaded into Hawaii.db")
    st.info(f"{len(df)} records inserted.")

except Exception as e:
    st.error(f"❌ Error: {e}")
