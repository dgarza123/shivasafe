import streamlit as st
import yaml

USERS_YAML_PATH = "users.yaml"

def load_users():
    try:
        with open(USERS_YAML_PATH, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def login(username, password):
    users = load_users()
    user = users.get(username)
    if user and user["password"] == password:
        st.session_state["user"] = username
        st.session_state["role"] = user.get("role", "viewer")
        return True
    return False

def logout():
    for key in ["user", "role"]:
        if key in st.session_state:
            del st.session_state[key]

def is_logged_in():
    return "user" in st.session_state

def current_user():
    return st.session_state.get("user", None)

def current_role():
    return st.session_state.get("role", "viewer")

def is_editor():
    return st.session_state.get("role") == "editor"

def require_editor():
    if not is_logged_in() or not is_editor():
        st.error("🔐 Editor access required.")
        st.stop()
