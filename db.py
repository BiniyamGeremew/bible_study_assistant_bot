import psycopg2
from config import DATABASE_URL 

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Function to save user
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

# Function to get total users
def get_total_users():
    cursor.execute("SELECT COUNT(*) FROM users;")
    return cursor.fetchone()[0]
