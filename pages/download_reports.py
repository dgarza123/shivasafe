import streamlit as st
from report_builder import generate_all_reports, zip_reports
import os

st.set_page_config(page_title="Download Reports", layout="wide")
st.title("🧾 Affidavit / Report Generator")

st.markdown("This tool generates a structured summary of all transactions from uploaded YAML files, enriched with TMK coordinates from `Hawaii.db`.")

# Button to trigger report generation
if st.button("🛠 Generate All Reports"):
    with st.spinner("Generating..."):
        report_files = generate_all_reports()
        if not report_files:
            st.warning("No valid YAML files found in /evidence/")
        else:
            zip_path = zip_reports(report_files)
            st.success(f"✅ {len(report_files)} reports generated.")
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="📦 Download All Reports (ZIP)",
                    data=f,
                    file_name="shivasafe_reports.zip",
                    mime="application/zip"
                )
