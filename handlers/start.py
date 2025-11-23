from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes
import random
import re
from utils.load_amharic_bible import load_amharic_bible

# ✅ Load Amharic Bible once at startup
bible_books_amharic = load_amharic_bible()

def escape_markdown_v2(text: str) -> str:
    """
    Escape all MarkdownV2 special characters.
    Required so Amharic text, emojis, and punctuation display safely.
    """
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def sanitize_username(name: str) -> str:
    """
    Fully sanitize Telegram username for MarkdownV2.
    Keep letters, numbers, spaces, and common emoji.
    Remove any characters that could break MarkdownV2.
    """
    if not name:
        return "God’s Child"
    
    # Remove characters that break MarkdownV2
    safe_name = re.sub(r'[_*\[\]()~`>#+\-=|{}.!<>/&]', '', name)
    
    # Remove control characters
    safe_name = re.sub(r'[\x00-\x1F\x7F]', '', safe_name)
    
    # Trim excessive whitespace
    safe_name = safe_name.strip()
    
    # If username becomes empty after sanitization, fallback
    return safe_name or "God’s Child"

def get_daily_verse():
    """Select a random verse from the Amharic Bible for today's verse."""
    book_name = random.choice(list(bible_books_amharic.keys()))
    chapters = bible_books_amharic[book_name]
    chapter = random.choice(chapters)
    verse_text = random.choice(chapter["verses"])
    verse_number = chapter["verses"].index(verse_text) + 1
    return verse_text.strip(), f"— {book_name} {chapter['chapter']}:{verse_number}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a personalized welcome message with a Markdown V2 blockquote verse."""
    user = update.effective_user
    verse_text, verse_ref = get_daily_verse()

    # Fully sanitize username to avoid MarkdownV2 errors
    safe_user_name = sanitize_username(user.first_name)
    
    # Escape all parts for MarkdownV2
    user_name = escape_markdown_v2(safe_user_name)
    verse_text_escaped = escape_markdown_v2(verse_text)
    verse_ref_escaped = escape_markdown_v2(verse_ref)
    feedback_text = escape_markdown_v2("💬 Feedback or Suggestions?")
    developer_text = escape_markdown_v2("Contact the developer 👉 @BiniyamGeremew")
    menu_instruction = escape_markdown_v2("Use the menu below to interact.")
    greeting_text = escape_markdown_v2(f"👋 Welcome to the Bible Study Assistant Bot, {user_name}! 🙏")
    todays_verse_text = escape_markdown_v2("📖 Today's Verse:")

    # 🧭 Main menu keyboard
    keyboard = [
        ["📖 Read Bible", "❓ Ask a Question"],
        ["🗓 Daily Verse / Notification", "ℹ️ About / Help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # 🕊️ Construct welcome message (same style as your original)
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
