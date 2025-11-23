import requests
from config import BIBLE_API_URL

def fetch_english_verse(reference):
    try:
        response = requests.get(f"{BIBLE_API_URL}/{reference}")
        if response.status_code == 200:
            data = response.json()
            return f"📖 {data['reference']}\n{data['text']}"
    except:
        pass
    return None
