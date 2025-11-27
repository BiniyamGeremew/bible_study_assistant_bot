from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes
from config import GITHUB_TOKEN

# Initialize GitHub OpenAI client
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=GITHUB_TOKEN
)

# Simple in-memory context storage
user_contexts = {}

# ---------------- Classify if the question is Bible-related ----------------
def is_bible_related(question: str) -> bool:
    """
    Uses a small AI call to classify whether a question is Bible-related.
    Returns True if the question is about the Bible, Jesus, Christianity, etc.
    """
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
        if isinstance(msg.content, list):
            decision = "".join([c.get("text", "") for c in msg.content])
        else:
            decision = msg.content or ""

        return "YES" in decision.upper()

    except Exception as e:
        print(f"Classification error: {e}")
        return True  # fallback to True if uncertain

# ---------------- STEP 2: Ask Question Handlers ----------------
async def ask_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please type your Bible-related question in English."
    )

async def ask_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text.strip()

    # Classify first
    if not is_bible_related(user_message):
        await update.message.reply_text(
            "🙏 Please ask *Bible-related* questions only.",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text("Thinking...")

    # Retrieve or initialize user context
    history = user_contexts.get(user_id, [])
    history.append({"role": "user", "content": user_message})

    # System prompt
    messages = [
        {
            "role": "system",
            "content": (
                "You are a Bible study assistant. Answer concisely (under 120 words). "
                "Base all responses ONLY on the Bible. Use simple, clear English. "
                "Connect follow-up questions naturally."
            )
        }
    ] + history

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=600  # can increase (response content length)
        )

        # ---------------- Robust content extraction ----------------
        msg = response.choices[0].message
        ai_answer = ""

        if hasattr(msg, "content"):
            if isinstance(msg.content, list):
                ai_answer = "".join([c.get("text", "") for c in msg.content])
            elif isinstance(msg.content, str):
                ai_answer = msg.content

        if not ai_answer.strip():
            ai_answer = "AI response was empty."

        # ---------------- Split long messages for Telegram ----------------
        MAX_TELEGRAM_LEN = 4000  # Telegram limit per message
        chunks = [ai_answer[i:i+MAX_TELEGRAM_LEN] for i in range(0, len(ai_answer), MAX_TELEGRAM_LEN)]
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode="Markdown")

        # Update user context (keep last 6 messages)
        history.append({"role": "assistant", "content": ai_answer})
        user_contexts[user_id] = history[-6:]

    except Exception as e:
        await update.message.reply_text(f"Error fetching response: {e}")

async def ask_question_callback(update, context):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Please type your Bible-related question again.")
