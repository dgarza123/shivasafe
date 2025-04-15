import streamlit as st
import yaml
import os

USERS_FILE = "users.yaml"

# Load users from YAML
try:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = yaml.safe_load(f) or {}
except FileNotFoundError:
    users = {}
    print("[LOGIN ERROR] users.yaml not found.")

# Authenticate and store session state
def login(username, password):
    user = users.get(username)
    if user and user["password"] == password:
        st.session_state["user"] = username
        st.session_state["role"] = user.get("role", "viewer")
        return True
    return False

# Check login status
def is_logged_in():
    return "user" in st.session_state

# Get current user or role
def current_user():
    return st.session_state.get("user")

def current_role():
    return st.session_state.get("role", "viewer")

# Logout
def logout():
    st.session_state.pop("user", None)
    st.session_state.pop("role", None)

# Enforce editor access
