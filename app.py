import streamlit as st
import os
import hashlib
import datetime
import shutil
import yaml

st.set_page_config(page_title="ShivaSafe Evidence Viewer", layout="wide")
st.title("ShivaSafe | Forensic Document Dashboard")

TMP_DIR = "tmp"

# --- Admin password protection ---
ADMIN_PASSWORD = "shiva2024"
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    password = st.text_input("Admin Access (Password Required):", type="password")
    if password == ADMIN_PASSWORD:
        st.session_state.auth = True
        st.experimental_rerun()
    else:
        st.stop()

# --- Upload Form (Admin Only) ---
with st.expander("Upload Forensic Evidence", expanded=False):
    with st.form("upload_form", clear_on_submit=True):
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf")
        yaml_file = st.file_uploader("Upload YAML", type=["yaml", "yml"], key="yaml")
        submit = st.form_submit_button("Submit")

        if submit and pdf_file and yaml_file:
            with st.spinner("Processing..."):
                file_bytes = pdf_file.read()
                file_hash = hashlib.sha256(file_bytes).hexdigest()
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
                base_name = f"{timestamp}_{file_hash[:12]}"

                # Save files
                os.makedirs(TMP_DIR, exist_ok=True)
                with open(os.path.join(TMP_DIR, base_name + ".pdf"), "wb") as f:
                    f.write(file_bytes)
                with open(os.path.join(TMP_DIR, base_name + "_entities.yaml"), "wb") as f:
                    f.write(yaml_file.read())

                st.success(f"Saved as `{base_name}`")
                st.experimental_rerun()

# --- Load Uploaded Evidence ---
pdfs = [f for f in os.listdir(TMP_DIR) if f.endswith(".pdf")]
yamls = [f for f in os.listdir(TMP_DIR) if f.endswith("_entities.yaml")]
yamls.sort(reverse=True)

# --- Display Files and Results ---
for yaml_file in yamls:
    try:
        yaml_path = os.path.join(TMP_DIR, yaml_file)
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        st.error(f"Failed to load {yaml_file}: {e}")
        continue

    pdf_name = yaml_file.replace("_entities.yaml", ".pdf")
    pdf_path = os.path.join(TMP_DIR, pdf_name)
    if not os.path.exists(pdf_path):
        continue

    with st.container():
        st.subheader(data.get("document", pdf_name))
        st.markdown(f"**SHA256**: `{data.get('sha256', '')[:16]}...`")
        st.markdown(f"**Creation Date**: `{data.get('creation_date', '—')}`")

        # Risk overview
        if "risk_score" in data:
            st.markdown("### Risk Score")
            st.write(data["risk_score"])

        # Entity overview
        if "entities" in data:
            st.markdown("### Key Entities")
            for e in data["entities"]:
                name = e.get("name") or e.get("email") or e.get("account_number", "")
                role = e.get("role", "")
                note = e.get("note", "")
                st.markdown(f"- **{name}** — _{role}_  {note}")

        # Transactions table
        if "transactions" in data:
            st.markdown("### Transactions")
            for tx in data["transactions"]:
                grantor = tx.get("grantor", "—")
                grantee = tx.get("grantee", "—")
                amount = tx.get("amount", "—")
                tmk = tx.get("parcel_id", "—")
                valid = "✅" if tx.get("parcel_valid") else "❌"
                st.markdown(f"- `{grantor}` → `{grantee}` | `{amount}` | {tmk} | Parcel Valid: {valid}")

        with st.expander("View YAML", expanded=False):
            st.code(yaml.dump(data, allow_unicode=True), language="yaml")
