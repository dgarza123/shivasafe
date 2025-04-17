for txn in transactions:
    if not isinstance(txn, dict):
        print(f"[!] Skipped invalid transaction in {fname}: {txn}")
        continue

    parcel = txn.get("parcel") or txn.get("parcel_id")
    grantee = txn.get("grantee") or txn.get("recipient")
    amount = txn.get("amount") or txn.get("value")
    date = txn.get("date")
    vis_2015, vis_2018, vis_2022, vis_2025 = get_visibility_flags(txn)

    c.execute("""
        INSERT INTO parcels (
            certificate_id, parcel_id, sha256, grantee, amount, date,
            present_2015, present_2018, present_2022, present_2025
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_id, parcel, sha256, grantee, amount, date,
        vis_2015, vis_2018, vis_2022, vis_2025
    ))
