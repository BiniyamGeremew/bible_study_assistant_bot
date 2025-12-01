import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")  
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Bot is running", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200

# Example bot handler
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Hello, welcome to the bot!")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
