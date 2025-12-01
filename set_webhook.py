import os
import requests

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = "https://bible-study-assistant-bot.onrender.com/webhook"

response = requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
print(response.json())
