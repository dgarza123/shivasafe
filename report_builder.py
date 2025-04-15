
import os
import yaml
import zipfile
import sqlite3
from datetime import datetime
from hawaii_db import get_coordinates_by_tmk

REPORTS_DIR = "reports"
EVIDENCE_DIR = "evidence"

os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_report_from_yaml(yaml_path):
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        base_name = os.path.splitext(os.path.basename(yaml_path))[0].replace("_entities", "")
        sha = data.get("sha256", "unknown")
        pdf = data.get("document", f"{base_name}.pdf")
        txs = data.get("transactions", [])

        lines = [f"# Forensic Report for `{pdf}`", ""]
        lines.append(f"SHA256: `{sha}`")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        for i, tx in enumerate(txs, 1):
            tmk = str(tx.get("parcel_id", "")).strip()
            coords = get_coordinates_by_tmk(tmk)
            lines.append(f"## Transaction {i}")
            lines.append(f"- **Grantor**: {tx.get('grantor', '')}")
            lines.append(f"- **Grantee**: {tx.get('grantee', '')}")
            lines.append(f"- **Amount**: {tx.get('amount', '')}")
            lines.append(f"- **Parcel ID**: `{tmk}`")
            lines.append(f"- **Valid Parcel**: {'✅' if tx.get('parcel_valid', True) else '❌'}")
            if coords:
                lines.append(f"- **Coordinates**: `{coords[0]:.5f}, {coords[1]:.5f}`")
            else:
                lines.append(f"- **Coordinates**: _Not found in Hawaii.db_")
            if tx.get("registry_key"):
                lines.append(f"- **Registry Key**: `{tx['registry_key']}`")
            if tx.get("offshore_note"):
                lines.append(f"- **Offshore Note**: _{tx['offshore_note']}_")
            lines.append("")

        report_path = os.path.join(REPORTS_DIR, f"{base_name}_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return report_path

    except Exception as e:
        return f"Failed to generate report: {e}"

def generate_all_reports():
    report_files = []
    for fname in os.listdir(EVIDENCE_DIR):
        if fname.endswith("_entities.yaml"):
            path = os.path.join(EVIDENCE_DIR, fname)
            report_path = generate_report_from_yaml(path)
            if report_path.endswith(".md"):
                report_files.append(report_path)
    return report_files

def zip_reports(report_paths, zip_name="shivasafe_reports.zip"):
    zip_path = os.path.join(REPORTS_DIR, zip_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in report_paths:
            zipf.write(path, arcname=os.path.basename(path))
    return zip_path
