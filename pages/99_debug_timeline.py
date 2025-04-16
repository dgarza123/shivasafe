# ✅ Diagnostic script to validate TMK suppression timeline input

import pandas as pd
import os

folder = "data"
files = ["Hawaii2018.csv", "Hawaii2022.csv", "Hawaii2025.csv"]

for fname in files:
    path = os.path.join(folder, fname)
    print(f"\n--- {fname} ---")

    if not os.path.exists(path):
        print("❌ File not found.")
        continue

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    print("Columns:", df.columns.tolist())
    if "TMK" not in df.columns:
        print("❌ 'TMK' column is missing.")
        continue

    df["TMK"] = df["TMK"].astype(str).str.strip()
    print("First 5 TMK values:", df["TMK"].head().tolist())
    print("Total TMKs:", len(df))
    print("Unique TMKs:", df["TMK"].nunique())
    print("Blank TMKs:", df["TMK"].isnull().sum() + (df["TMK"] == "").sum())
