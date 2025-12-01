import os
import telebot
from flask import Flask, request

# ------------------ Bot Setup ------------------
TOKEN = os.getenv("BOT_TOKEN")  
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Health check route for UptimeRobot
@app.route('/', methods=['GET'])
def home():
    return "Bot is running", 200

# Webhook route for Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200


@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Hello, welcome to the bot!")


