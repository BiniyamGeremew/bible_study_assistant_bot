from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import BOT_TOKEN
from handlers.start import start
from handlers.bible_reading import read_bible_handler, callback_dispatcher
from handlers.ask_question import ask_question_start, ask_question_handler, ask_question_callback
from handlers.search import verse_command  

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("verse", verse_command))
app.add_handler(MessageHandler(filters.Regex("^📖 Read Bible$"), read_bible_handler))
app.add_handler(MessageHandler(filters.Regex("^❓ Ask a Question$"), ask_question_start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ask_question_handler))
app.add_handler(CallbackQueryHandler(callback_dispatcher))
app.add_handler(CallbackQueryHandler(ask_question_callback))

print("✅ Bible Study Assistant Bot is running...")
app.run_polling()
