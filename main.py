from datetime import time, timedelta
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
import asyncio

app = Application.builder().token(BOT_TOKEN).build()

# ------------------ Register Handlers ------------------
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Regex("^📖 Read Bible$"), read_bible_handler))
app.add_handler(MessageHandler(filters.Regex("^❓ Ask a Question$"), ask_question_start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ask_question_handler))
app.add_handler(CallbackQueryHandler(callback_dispatcher))
app.add_handler(CallbackQueryHandler(ask_question_callback))

# ------------------ Job Queue ------------------
job_queue = app.job_queue

# send daily verse at 12:00 AM Ethiopia time (UTC+3)
job_queue.run_daily(
    send_daily_verse,
    time=time(hour=21, minute=0, second=0),  
    name="daily_verse"
)


print("✅ Bible Study Assistant Bot is running...")
app.run_polling()
