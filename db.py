import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")  # get from env variables

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

def save_user(user):
    user_id = str(user.id)
    username = user.username or ""
    cursor.execute("""
        INSERT INTO users (user_id, username)
        VALUES (%s, %s)
        ON CONFLICT (user_id) DO UPDATE
        SET username = EXCLUDED.username;
    """, (user_id, username))
    conn.commit()

def get_total_users():
    cursor.execute("SELECT COUNT(*) FROM users;")
    result = cursor.fetchone()
    return result[0] if result else 0
