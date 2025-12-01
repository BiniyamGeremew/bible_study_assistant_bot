from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes
from config import GITHUB_TOKEN
from rapidfuzz import fuzz, process

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=GITHUB_TOKEN
)

# In-memory user context
user_contexts = {}

# Bible-related keywords for fuzzy matching and suggestions
BIBLE_KEYWORDS = [
    "jesus", "christ", "bible", "god", "mary", "apostle", "moses",
    "abraham", "faith", "church", "sin", "heaven", "hell"
]

# ---------------- Helper: Suggest Bible topics ----------------
def suggest_bible_topic(user_message: str, limit: int = 3):
    """
    Suggest possible Bible keywords/topics based on user message.
    Returns top matches with similarity >= 80%.
    """
    matches = process.extract(user_message.lower(), BIBLE_KEYWORDS, scorer=fuzz.partial_ratio, limit=limit)
    suggestions = [match[0] for match in matches if match[1] >= 60]
    return suggestions

# ---------------- Classify Bible-related questions ----------------
def is_bible_related(question: str):
    """
    Determines if a question is Bible-related.
    Uses fuzzy keyword matching first, then AI classification as fallback.
    Returns: (bool, suggestions_list)
    """
    suggestions = suggest_bible_topic(question)
    if suggestions:
        return True, suggestions

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a classifier. Reply ONLY with 'YES' or 'NO'. "
                        "If uncertain, reply 'YES'. The question is about the Bible, Jesus, God, "
                        "Christianity, or biblical events."
                    )
                },
                {"role": "user", "content": question}
            ],
            temperature=0,
            max_tokens=2
        )

        msg = response.choices[0].message
        decision = msg.content if isinstance(msg.content, str) else "".join(c.get("text", "") for c in msg.content)
        return "YES" in decision.upper(), []

    except Exception as e:
        print(f"Classification error: {e}")
        return True, []

# ---------------- Telegram Handlers ----------------
async def ask_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please type your Bible-related question in English."
    )

async def ask_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text.strip()

    # Check if Bible-related and get suggestions
    related, suggestions = is_bible_related(user_message)
    if not related:
        msg_text = "🙏 Please ask *Bible-related* questions only."
        if suggestions:
            msg_text += f" Did you mean: {', '.join(suggestions)}?"
        await update.message.reply_text(msg_text, parse_mode="Markdown")
        return

    await update.message.reply_text("Thinking...")

    # Retrieve user context or initialize
    history = user_contexts.get(user_id, [])
    history.append({"role": "user", "content": user_message})

    # System prompt enforcing English and allowing biblical violent events
    messages = [
        {
            "role": "system",
            "content": (
                "You are a Bible study assistant. Answer concisely (under 200 words). "
                "Base all responses ONLY on the Bible. Use simple, clear English. "
                "You may describe violent events if they appear in the Bible for educational or spiritual context. "
                "Do NOT respond in any other language. Connect follow-up questions naturally."
            )
        }
    ] + history

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )

        msg = response.choices[0].message
        ai_answer = ""
        if hasattr(msg, "content"):
            if isinstance(msg.content, list):
                ai_answer = "".join([c.get("text", "") for c in msg.content])
            elif isinstance(msg.content, str):
                ai_answer = msg.content

        # Fallback if empty
        if not ai_answer.strip():
            ai_answer = (
                "🙏 Your question contains content that Azure's moderation system flagged as restricted. "
                "Please rephrase your question or use alternative wording."
            )

        # Split long messages for Telegram
        MAX_TELEGRAM_LEN = 4000
        chunks = [ai_answer[i:i + MAX_TELEGRAM_LEN] for i in range(0, len(ai_answer), MAX_TELEGRAM_LEN)]
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode="Markdown")

        # Update context (keep last 6 messages)
        history.append({"role": "assistant", "content": ai_answer})
        user_contexts[user_id] = history[-6:]

    except Exception as e:
        error_str = str(e)
        # Handle Azure moderation errors gracefully
        if "content_filter" in error_str or "ResponsibleAIPolicyViolation" in error_str:
            await update.message.reply_text(
                "🙏 Your question contains content that Azure's moderation system flagged as restricted. "
                "Please rephrase your question or use alternative wording."
            )
        else:
            await update.message.reply_text(f"Error fetching response: {e}")


async def ask_question_callback(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please type your Bible-related question again.")
