from datetime import time
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from config import BOT_TOKEN
from handlers.start import start
from handlers.bible_reading import read_bible_handler, callback_dispatcher
from handlers.ask_question import (
    ask_question_start,
    ask_question_handler,
    ask_question_callback,
)
from handlers.daily_verse_sender import send_daily_verse
from db import save_user  # <-- import the save_user function

# ------------------ Init App ------------------
app = Application.builder().token(BOT_TOKEN).build()

# ------------------ Wrap start handler to save user ------------------
async def start_and_save(update, context):
    user = update.effective_user
    save_user(user)  # Save user to DB (sync is fine)
    await start(update, context)  # Await the original async start handler

# ------------------ Message Handlers ------------------
app.add_handler(CommandHandler("start", start_and_save))  # updated wrapper
app.add_handler(MessageHandler(filters.Regex("^📖 Read Bible$"), read_bible_handler))
app.add_handler(MessageHandler(filters.Regex("^❓ Ask a Question$"), ask_question_start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ask_question_handler))

# ------------------ Callback Handlers ------------------
app.add_handler(
    CallbackQueryHandler(callback_dispatcher, pattern="^(version_|book_|chapter_|back_).*")
)
app.add_handler(
    CallbackQueryHandler(ask_question_callback, pattern="^ask_.*")
)

# ------------------ Job Queue ------------------
job_queue = app.job_queue

# 12:00 AM Ethiopia time = 21:00 UTC
job_queue.run_daily(
    send_daily_verse,
    time=time(hour=21, minute=0, second=0),
    name="daily_verse"
)

print("✅ Bible Study Assistant Bot is running...")
app.run_polling()
