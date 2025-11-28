# Bible Study Assistant Bot

A Telegram bot that helps users read the Bible in English and Amharic, ask Bible-related questions using AI, and receive daily verses. Built with Python and the `python-telegram-bot` library. Models used: `openai/gpt-4o-mini` for classification and `openai/gpt-4o` for answers via GitHub-hosted OpenAI models: https://models.github.ai/inference.

## Features
- 📖 Read Bible in English or Amharic  
- ❓ Ask Bible-related questions in English, powered by AI  
  - Uses `openai/gpt-4o-mini` for fast yes/no classification of Bible-related questions  
  - Uses `openai/gpt-4o` for generating concise, context-aware Bible answers  
- 📅 Receive daily Bible verses automatically  
- Multi-language support and Markdown-formatted responses  
- Simple, interactive Telegram menus  

> Models Source: GitHub-hosted OpenAI models from the [GitHub Marketplace](https://github.com/marketplace?type=models). Models are accessed via the OpenAI Python library using GitHub’s inference endpoint: `https://models.github.ai/inference`.

## Installation and Setup

1. **Clone the repository**  
git clone https://github.com/BiniyamGeremew/bible-study-assistant-bot.git && cd bible-study-assistant-bot

2. **Create and activate virtual environment**  
python -m venv venv && source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**  
pip install -r requirements.txt

4. **Set up environment variables**  
Create `config.py` and replace placeholders:  
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  
BIBLE_API_URL = "https://bible-api.com"  
GITHUB_TOKEN = "YOUR_GITHUB_OPENAI_TOKEN"

5. **Run the bot**  
python main.py

## Requirements
python-telegram-bot==20.3  
requests==2.31.0  
python-dotenv==1.0.1  
openai>=1.42.0

## Usage
Open Telegram, start a chat with your bot, use the menu to read Bible chapters in English or Amharic, ask Bible-related questions, and receive daily verses automatically.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
