import re
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.load_amharic_bible import load_amharic_bible
from config import BIBLE_API_URL

# Load Amharic Bible
bible_books_amharic = load_amharic_bible()

# English KJV books and their chapter counts
ENGLISH_BIBLE_BOOKS = [
    "Genesis","Exodus","Leviticus","Numbers","Deuteronomy","Joshua","Judges","Ruth",
    "1 Samuel","2 Samuel","1 Kings","2 Kings","1 Chronicles","2 Chronicles","Ezra",
    "Nehemiah","Esther","Job","Psalms","Proverbs","Ecclesiastes","Song of Solomon",
    "Isaiah","Jeremiah","Lamentations","Ezekiel","Daniel","Hosea","Joel","Amos","Obadiah",
    "Jonah","Micah","Nahum","Habakkuk","Zephaniah","Haggai","Zechariah","Malachi",
    "Matthew","Mark","Luke","John","Acts","Romans","1 Corinthians","2 Corinthians",
    "Galatians","Ephesians","Philippians","Colossians","1 Thessalonians","2 Thessalonians",
    "1 Timothy","2 Timothy","Titus","Philemon","Hebrews","James","1 Peter","2 Peter",
    "1 John","2 John","3 John","Jude","Revelation"
]

ENGLISH_CHAPTER_COUNTS = {
    "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
    "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
    "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36, "Ezra": 10,
    "Nehemiah": 13, "Esther": 10, "Job": 42, "Psalms": 150, "Proverbs": 31,
    "Ecclesiastes": 12, "Song of Solomon": 8, "Isaiah": 66, "Jeremiah": 52,
    "Lamentations": 5, "Ezekiel": 48, "Daniel": 12, "Hosea": 14, "Joel": 3,
    "Amos": 9, "Obadiah": 1, "Jonah": 4, "Micah": 7, "Nahum": 3, "Habakkuk": 3,
    "Zephaniah": 3, "Haggai": 2, "Zechariah": 14, "Malachi": 4, "Matthew": 28,
    "Mark": 16, "Luke": 24, "John": 21, "Acts": 28, "Romans": 16, "1 Corinthians": 16,
    "2 Corinthians": 13, "Galatians": 6, "Ephesians": 6, "Philippians": 4,
    "Colossians": 4, "1 Thessalonians": 5, "2 Thessalonians": 3, "1 Timothy": 6,
    "2 Timothy": 4, "Titus": 3, "Philemon": 1, "Hebrews": 13, "James": 5, "1 Peter": 5,
    "2 Peter": 3, "1 John": 5, "2 John": 1, "3 John": 1, "Jude": 1, "Revelation": 22
}

CHAPTERS_PER_PAGE = 50  # Max 50 chapters per page


# ---------------- Markdown Escaping ----------------
def escape_markdown_v2(text: str) -> str:
    """Escape all MarkdownV2 special characters for Telegram display."""
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)


# ---------------- Text Formatting Helper ----------------
def format_bible_message(book_name: str, chapter: int, verses: list, language: str = "en") -> str:
    """
    Format a Bible passage (multiple verses) with MarkdownV2 blockquote style.
    Works for both English and Amharic versions.
    """
    title = "📖 Chapter Reading:" if language == "en" else "📖 የዚህ ምዕራፍ ንባብ፦"
    title_md = escape_markdown_v2(title)

    formatted_verses = "\n".join(
        [f"> {escape_markdown_v2(v)}" for v in verses]
    )

    reference_md = escape_markdown_v2(f"— {book_name} {chapter}")

    return f"{title_md}\n\n{formatted_verses}\n\n{reference_md}"


# ---------------- Handlers ----------------
async def read_bible_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Step 1: Version selection"""
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data="version_english"),
            InlineKeyboardButton("Amharic", callback_data="version_amharic")
        ]
    ]
    await update.message.reply_text(
        "Choose Bible version:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- Callback Dispatcher ----------------
async def callback_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # ---------- Back Navigation ----------
    if data == "back_version":
        await show_version_menu(query, context)
        return
    if data == "back_book":
        version = context.user_data.get("version")
        if version:
            await show_books_menu(query, context, version)
        return
    if data.startswith("back_chapter"):
        version = context.user_data.get("version")
        book = context.user_data.get("book")
        page = int(data.split("_")[-1]) if "_" in data else 0
        if version and book:
            await show_chapters_menu(query, context, version, book, page)
        return

    # ---------- Chapter Pagination ----------
    if data.startswith("chapter_page_"):
        page = int(data.split("_")[-1])
        version = context.user_data.get("version")
        book = context.user_data.get("book")
        if version and book:
            await show_chapters_menu(query, context, version, book, page)
        return

    # ---------- Version Selection ----------
    if data.startswith("version_"):
        version = data.split("_")[1]
        context.user_data["version"] = version
        await show_books_menu(query, context, version)
        return

    # ---------- Book Selection ----------
    if data.startswith("book_"):
        _, version, book_name = data.split("_", 2)
        context.user_data["book"] = book_name
        await show_chapters_menu(query, context, version, book_name)
        return

    # ---------- Chapter Selection ----------
    if data.startswith("chapter_"):
        _, version, chapter = data.split("_")
        chapter = int(chapter)
        book = context.user_data.get("book")
        await show_verses(query, context, version, book, chapter)
        return


# ---------------- Helper Functions ----------------
async def show_version_menu(query, context):
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data="version_english"),
            InlineKeyboardButton("Amharic", callback_data="version_amharic")
        ]
    ]
    await query.message.edit_text(
        "Choose Bible version:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_books_menu(query, context, version):
    keyboard = []
    row = []
    books = ENGLISH_BIBLE_BOOKS if version == "english" else list(bible_books_amharic.keys())

    for i, book in enumerate(books, 1):
        row.append(InlineKeyboardButton(book, callback_data=f"book_{version}_{book}"))
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_version")])

    await query.message.edit_text(
        "Select a book:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_chapters_menu(query, context, version, book_name, page=0):
    if version == "english":
        num_chapters = ENGLISH_CHAPTER_COUNTS.get(book_name, 50)
    else:
        num_chapters = len(bible_books_amharic[book_name])

    start = page * CHAPTERS_PER_PAGE + 1
    end = min(start + CHAPTERS_PER_PAGE - 1, num_chapters)

    keyboard = []
    row = []
    for i in range(start, end + 1):
        row.append(InlineKeyboardButton(str(i), callback_data=f"chapter_{version}_{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    pagination_row = []
    if start > 1:
        pagination_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"chapter_page_{page-1}"))
    if end < num_chapters:
        pagination_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"chapter_page_{page+1}"))
    if pagination_row:
        keyboard.append(pagination_row)

    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_book")])

    context.user_data["chapter_page"] = page

    await query.message.edit_text(
        f"Select a chapter in {book_name} ({start}-{end}/{num_chapters}):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_verses(query, context, version, book, chapter):
    MAX_VERSES = 15
    if version == "english":
        reference = f"{book} {chapter}"
        try:
            response = requests.get(f"{BIBLE_API_URL}/{reference}")
            if response.status_code == 200:
                data = response.json()
                verse_texts = [
                    f"{v['verse']}. {re.sub(r'\\s+', ' ', v['text']).strip()}"
                    for v in data["verses"]
                ]
                chunks = [verse_texts[i:i + MAX_VERSES] for i in range(0, len(verse_texts), MAX_VERSES)]
                for chunk in chunks:
                    message = format_bible_message(book, chapter, chunk, language="en")
                    await query.message.reply_text(message, parse_mode="MarkdownV2")
            else:
                await query.message.reply_text("❌ Could not fetch chapter.")
        except Exception:
            await query.message.reply_text("❌ API error.")
    else:
        chapters_list = bible_books_amharic[book]
        chapter_obj = next((c for c in chapters_list if int(c["chapter"]) == chapter), None)
        if chapter_obj:
            verse_texts = [f"{i+1}. {v.replace('\\n', ' ').strip()}" for i, v in enumerate(chapter_obj["verses"])]
            chunks = [verse_texts[i:i + MAX_VERSES] for i in range(0, len(verse_texts), MAX_VERSES)]
            for chunk in chunks:
                message = format_bible_message(book, chapter, chunk, language="am")
                await query.message.reply_text(message, parse_mode="MarkdownV2")
        else:
            await query.message.reply_text("❌ Could not find chapter.")

    page = context.user_data.get("chapter_page", 0)
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data=f"back_chapter_{page}")]]
    await query.message.reply_text(
        f"Back to {book} chapters:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
