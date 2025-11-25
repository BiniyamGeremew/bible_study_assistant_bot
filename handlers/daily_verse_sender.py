import json
import os
import random
from utils.load_amharic_bible import load_amharic_bible

# Load Amharic Bible once
bible_books_amharic = load_amharic_bible()

DATA_FILE = "data/users.json"
BOT_USERNAME = "bible_study_assistant_bot" 


def get_random_verse():
    """Get random Amharic verse."""
    book_name = random.choice(list(bible_books_amharic.keys()))
    chapters = bible_books_amharic[book_name]

    chapter = random.choice(chapters)
    verse_text = random.choice(chapter["verses"])
    verse_number = chapter["verses"].index(verse_text) + 1

    return verse_text.strip(), f"— {book_name} {chapter['chapter']}:{verse_number}"

# ------------------ Send Daily Verse ------------------
async def send_daily_verse(context):
    """Send daily verse to all users (plain text, with bot username)."""
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    if not users:
        return

    verse, ref = get_random_verse()

    # Compose message including bot username 
    text = f"📖 የዛሬ የመጽሐፍ ቅዱስ ጥቅስ\n\n{verse}\n\n{ref}\n\n@{BOT_USERNAME}"
    for chat_id in users:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text
            )
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
