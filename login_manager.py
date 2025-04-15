import streamlit as st
import yaml
import os

USERS_FILE = "users.yaml"

# Load user accounts from YAML
try:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = yaml.safe_load(f) or {}
except FileNotFoundError:
    users = {}
    print("[LOGIN ERROR] users.yaml not found.")

def login(username, password):
    user = users.get(username)
    if user and user["password"] == password:
        st.session_state["user"] = username
        st.session_state["role"] = user.get("role", "viewer")
        return True
    return False

def require_editor():
    if "user" not in st.session_state or st.session_state.get("role") != "editor":
        st.error("🔐 Editor access required.")
        st.stop()

def is_editor():
    return st.session_state.get("role") == "editor"

def current_user():
    return st.session_state.get("user")
