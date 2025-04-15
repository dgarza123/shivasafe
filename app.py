import streamlit as st
from login_manager import is_logged_in, current_role

st.set_page_config(page_title="ShivaSafe Public Viewer", layout="centered")

st.title("ShivaSafe Forensic Land Viewer")

st.markdown("""
Welcome to **ShivaSafe** — the public transparency tool exposing concealed land transfers and offshore trust routing within Hawaii’s property system.

---

### What Is This?
This platform reveals hidden financial flows, registry key transfers, and non-rendered certificate data extracted from digitally obfuscated documents. These records are not visible in traditional government systems and were recovered using advanced forensic decoding.

---

### What You’ll Find:
- **Registry keys**, escrow IDs, and suppressed offshore transfer records
- Entities such as **Science of Identity Foundation** and **Shiva Escrow Holdings**
- Concealed flows to offshore banks including **BDO (Philippines)** and **HSBC (Singapore)**

---

### Technical Methodology:
- CID font reversal, ligature recovery, XOR stream decoding
- Mapping of unlisted TMK parcels to geocoordinates
- Auto-tagging of grantee, parcel, and escrow metadata

---

### Evidence Sections:
- [🧾 Transaction Timeline](timeline)
- [📍 Offshore Routing Map](map_viewer)
""")

# Conditional display of Admin Panel link
if is_logged_in() and current_role() == "editor":
    st.markdown("- [🔐 Admin Panel](admin_home)")

st.markdown("""
---

**Disclaimer:** This site presents digitally suppressed content recovered from PDF document layers not visible via traditional rendering tools. All data has been recovered using forensic methods and presented for public analysis and legal validation.

---

© 2025 ShivaSafe. No claim to ownership or authenticity is made beyond forensic extraction.
""")