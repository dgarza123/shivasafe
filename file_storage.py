import os
from pathlib import Path
import hashlib
import yaml

EVIDENCE_DIR = Path("evidence")
EVIDENCE_DIR.mkdir(exist_ok=True)

def save_uploaded_pair(yaml_file, pdf_file):
    if not yaml_file.name.endswith(".yaml") and not yaml_file.name.endswith(".yml"):
        raise ValueError("First file must be a YAML")
    if not pdf_file.name.endswith(".pdf"):
        raise ValueError("Second file must be a PDF")

    base_name = Path(yaml_file.name).stem
    case_dir = EVIDENCE_DIR / base_name
    case_dir.mkdir(parents=True, exist_ok=True)

    # Save YAML
    yaml_path = case_dir / yaml_file.name
    yaml_bytes = yaml_file.read()
    with open(yaml_path, "wb") as f:
        f.write(yaml_bytes)
    parsed_yaml = yaml.safe_load(yaml_bytes.decode("utf-8"))

    # Save PDF
    pdf_path = case_dir / pdf_file.name
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.read())

    # Add metadata
    parsed_yaml["_uploaded_filename"] = yaml_file.name
    parsed_yaml["_sha256"] = hashlib.sha256(yaml_bytes).hexdigest()
    parsed_yaml["_pdf_path"] = str(pdf_path)

    return parsed_yaml

def list_saved_cases():
    cases = []
    for folder in EVIDENCE_DIR.iterdir():
        if folder.is_dir():
            yaml_files = list(folder.glob("*.yml")) + list(folder.glob("*.yaml"))
            for yml in yaml_files:
                try:
                    with open(yml, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        data["_folder"] = str(folder)
                        cases.append(data)
                except Exception as e:
                    print(f"Failed to load {yml}: {e}")
    return cases
