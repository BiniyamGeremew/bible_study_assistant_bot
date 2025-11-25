import json
import os

USER_FILE = "users.json"


def load_users():
    """Load all registered users."""
    if not os.path.exists(USER_FILE):
        return []

    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_user(chat_id: int):
    """Save a user ID only if not already saved."""
    users = load_users()

    if chat_id not in users:
        users.append(chat_id)

        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
