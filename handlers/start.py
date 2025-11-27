from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes
import random
import re
import json
import os
from utils.load_amharic_bible import load_amharic_bible

# Load Amharic Bible once at startup
bible_books_amharic = load_amharic_bible()

# User storage file for daily verse system
DATA_FILE = "data/users.json"


def save_user(chat_id):
    os.makedirs("data", exist_ok=True)

    users = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)

    if chat_id not in users:
        users.append(chat_id)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

def escape_markdown_v2(text: str) -> str:
    #Escape MarkdownV2 special characters
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def sanitize_username(name: str) -> str:
    if not name:
        return "God’s Child"
    
    safe_name = re.sub(r'[_*\[\]()~`>#+\-=|{}.!<>/&]', '', name)
    safe_name = re.sub(r'[\x00-\x1F\x7F]', '', safe_name)
    safe_name = safe_name.strip()
    return safe_name or "God’s Child"


def get_daily_verse():
    #Select a random Amharic Bible verse
    book_name = random.choice(list(bible_books_amharic.keys()))
    chapters = bible_books_amharic[book_name]
    chapter = random.choice(chapters)
    verse_text = random.choice(chapter["verses"])
    verse_number = chapter["verses"].index(verse_text) + 1
    return verse_text.strip(), f"— {book_name} {chapter['chapter']}:{verse_number}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
   #Send welcome message with a random verse
    user = update.effective_user

    save_user(update.effective_chat.id)

    verse_text, verse_ref = get_daily_verse()

    safe_user_name = sanitize_username(user.first_name)

    user_name = escape_markdown_v2(safe_user_name)
    verse_text_escaped = escape_markdown_v2(verse_text)
    verse_ref_escaped = escape_markdown_v2(verse_ref)
    feedback_text = escape_markdown_v2("💬 Feedback or Suggestions?")
    developer_text = escape_markdown_v2("Contact the developer 👉 @BiniyamGeremew")
    menu_instruction = escape_markdown_v2("Use the menu below to interact.")
    greeting_text = escape_markdown_v2(f"👋 Welcome to the Bible Study Assistant Bot, {user_name}! 🙏")
    todays_verse_text = escape_markdown_v2("📖 Today's Verse:")

    keyboard = [
        ["📖 Read Bible", "❓ Ask a Question"],
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome_text = (
        f"{greeting_text}\n\n"
        f"{todays_verse_text}\n\n"
        f"> {verse_text_escaped}\n\n"
        f"{verse_ref_escaped}\n\n"
        f"{menu_instruction}\n\n"
        f"{feedback_text}\n"
        f"{developer_text}"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )

    context.user_data["step"] = "main_menu"
