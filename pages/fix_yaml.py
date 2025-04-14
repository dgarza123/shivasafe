import streamlit as st
import os
import yaml
import shutil

st.set_page_config(page_title="YAML Structure Fixer", layout="wide")
st.title("Admin: YAML Structure Fixer")

# Load admin password
CONFIG_PATH = "config.yaml"
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
ADMIN_PASSWORD = config.get("admin_password")

if "auth_fix_yaml" not in st.session_state:
    st.session_state.auth_fix_yaml = False

if not st.session_state.auth_fix_yaml:
    password = st.text_input("Enter admin password:", type="password")
    if password == ADMIN_PASSWORD:
        st.session_state.auth_fix_yaml = True
        st.rerun()
    else:
        st.stop()

# Fix function
def fix_yaml_structure():
    EVIDENCE_DIR = "evidence"
    fixed = []
    skipped = []
    errors = []

    for fname in os.listdir(EVIDENCE_DIR):
        if not fname.endswith("_entities.yaml"):
            continue

        fpath = os.path.join(EVIDENCE_DIR, fname)

        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if isinstance(data, dict) and "transactions" in data:
                skipped.append(fname)
                continue

            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                # Backup original
                backup_path = fpath.replace("_entities.yaml", "_invalid.yaml")
                shutil.move(fpath, backup_path)

                wrapped = {
                    "sha256": "placeholder",
                    "document": fname.replace("_entities.yaml", ".pdf"),
                    "transactions": data,
                }

                with open(fpath, "w", encoding="utf-8") as out:
                    yaml.dump(wrapped, out, sort_keys=False)

                fixed.append(fname)
            else:
                skipped.append(fname)

        except Exception as e:
            errors.append(f"{fname}: {e}")

    return fixed, skipped, errors

# Trigger
if st.button("Scan and Fix YAML Structure"):
    fixed, skipped, errors = fix_yaml_structure()

    if fixed:
        st.success(f"Fixed: {len(fixed)} files")
        st.code("\n".join(fixed))
    else:
        st.info("No files required fixing.")

    if skipped:
        st.caption(f"Skipped: {len(skipped)} already valid")

    if errors:
        st.error("Errors encountered:")
        st.code("\n".join(errors))
