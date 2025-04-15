import streamlit as st
import yaml

def load_users():
    with open("users.yaml", "r") as f:
        return yaml.safe_load(f).get("users", [])

def login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None

    users = load_users()

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            for user in users:
                if user["username"] == username and user["password"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = user["role"]
                    st.success("Login successful.")
                    st.experimental_rerun()
            st.error("Invalid username or password.")

def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None
    st.success("Logged out.")
    st.experimental_rerun()

def is_logged_in():
    return st.session_state.get("logged_in", False)

def current_user():
    return st.session_state.get("username")

def current_role():
    return st.session_state.get("role", "viewer")

def require_editor():
    if not is_logged_in() or current_role() != "editor":
        st.error("Unauthorized access.")
        st.stop()
