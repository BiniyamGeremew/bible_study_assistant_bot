import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.load_amharic_bible import load_amharic_bible

bible_books_amharic = load_amharic_bible()

def get_random_amharic_verse():
    book_name = random.choice(list(bible_books_amharic.keys()))
    chapters = bible_books_amharic[book_name]
    chapter = random.choice(chapters)
    verse_text = random.choice(chapter["verses"]).strip()
    verse_number = chapter["verses"].index(verse_text) + 1
    reference = f"{book_name} {chapter['chapter']}:{verse_number}"
    return verse_text, reference

async def send_daily_verse(context):
    users = load_users()
    verse, ref = get_random_amharic_verse()

    share_btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Share", switch_inline_query=verse)]
    ])

    text = f"📖 ዛሬ የቀኑ እትም:\n\n{verse}\n\n— {ref}"

    for chat_id in users:
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=share_btn
            )
        except:
            pass
