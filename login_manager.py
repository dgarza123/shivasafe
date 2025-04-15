import yaml
import streamlit as st

USERS_YAML = "users.yaml"

def load_users():
    with open(USERS_YAML, "r") as f:
        data = yaml.safe_load(f)
    return data.get("users", {})

def login(username, password):
    users = load_users()
    user = users.get(username)
    if user and user.get("password") == password:
        st.session_state["username"] = username
        st.session_state["role"] = user.get("role", "viewer")
        return True
    return False

def logout():
    for key in ["username", "role"]:
        if key in st.session_state:
            del st.session_state[key]

def is_logged_in():
    return "username" in st.session_state

def current_user():
    return st.session_state.get("username")

def current_role():
    return st.session_state.get("role", "viewer")

def require_login():
    if not is_logged_in():
        st.error("You must be logged in to access this page.")
        st.stop()

def require_editor():
    if current_role() != "editor":
        st.error("You must be an editor to access this page.")
        st.stop()
