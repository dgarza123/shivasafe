import yaml
import os

USERS_FILE = "users.yaml"

with open(USERS_FILE, "r", encoding="utf-8") as f:
    users = yaml.safe_load(f)
