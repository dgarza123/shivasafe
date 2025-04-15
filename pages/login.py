import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from login_manager import login, logout, is_logged_in, current_user, current_role

st.set_page_config(page_title="Login", layout="centered")
st.title("🔐 Login")

# ✅ If already logged in
if is_logged_in():
    st.success(f"Logged in as: {current_user()} ({current_role()})")
    if st.button("Log out"):
        logout()
        st.rerun()

# ✅ If not logged in, show login form
else:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

        if submitted:
            if login(username, password):
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid credentials.")
