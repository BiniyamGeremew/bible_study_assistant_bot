import re
import requests
from difflib import get_close_matches
from telegram import Update
from telegram.ext import ContextTypes
from utils.load_amharic_bible import load_amharic_bible
from config import BIBLE_API_URL  # English Bible API

# Load Amharic Bible
bible_books_amharic = load_amharic_bible()

# Map Amharic book filenames to readable names
AMHARIC_BOOKS = [ 
    "ዘፍጥረት","ዘጸአት","ዘሌዋውያን","ዘኍልቍ","ዘዳግም","መጽሐፈ ኢያሱ ወልደ ነዌ",
    "መጽሐፈ መሣፍንት","መጽሐፈ ሩት","መጽሐፈ ሳሙኤል ቀዳማዊ","መጽሐፈ ሳሙኤል ካል",
    "መጽሐፈ ነገሥት ቀዳማዊ።","መጽሐፈ ነገሥት ካልዕ።","መጽሐፈ ዜና መዋዕል ቀዳማዊ።",
    "መጽሐፈ ዜና መዋዕል ካልዕ።","መጽሐፈ ዕዝራ።","መጽሐፈ ነህምያ።","መጽሐፈ አስቴር።",
    "መጽሐፈ ኢዮብ።","መዝሙረ ዳዊት","መጽሐፈ ምሳሌ","መጽሐፈ መክብብ",
    "መኃልየ መኃልይ ዘሰሎሞን","ትንቢተ ኢሳይያስ","ትንቢተ ኤርምያስ","ሰቆቃው ኤርምያስ",
    "ትንቢተ ሕዝቅኤል","ትንቢተ ዳንኤል","ትንቢተ ሆሴዕ","ትንቢተ ኢዮኤል","ትንቢተ አሞጽ",
    "ትንቢተ አብድዩ","ትንቢተ ዮናስ","ትንቢተ ሚክያስ","ትንቢተ ናሆም","ትንቢተ ዕንባቆም",
    "ትንቢተ ሶፎንያስ","ትንቢተ ሐጌ","ትንቢተ ዘካርያስ","ትንቢተ ሚልክያ","የማቴዎስ ወንጌል",
    "የማርቆስ ወንጌል","የሉቃስ ወንጌል","የዮሐንስ ወንጌል","የሐዋርያት ሥራ","ወደ ሮሜ ሰዎች",
    "1ኛ ወደ ቆሮንቶስ ሰዎች","2ኛ ወደ ቆሮንቶስ ሰዎች","ወደ ገላትያ ሰዎች","ወደ ኤፌሶን ሰዎች",
    "ወደ ፊልጵስዩስ ሰዎች","ወደ ቆላስይስ ሰዎች","1ኛ ወደ ተሰሎንቄ ሰዎች","2ኛ ወደ ተሰሎንቄ ሰዎች",
    "1ኛ ወደ ጢሞቴዎስ","2ኛ ወደ ጢሞቴዎስ","ወደ ቲቶ","ወደ ፊልሞና","ወደ ዕብራውያን",
    "የያዕቆብ መልእክት","1ኛ የጴጥሮስ መልእክት","2ኛ የጴጥሮስ መልእክት","1ኛ የዮሐንስ መልእክት",
    "2ኛ የዮሐንስ መልእክት","3ኛ የዮሐንስ መልእክት","የይሁዳ መልእክት","የዮሐንስ ራእይ"
]

# English Bible books
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

# ---------- Book Finder with Fuzzy Search ----------
def find_book(name: str):
    name = name.strip()

    # ---------- English ----------
    if name in ENGLISH_BIBLE_BOOKS:
        return "EN", name
    en_match = get_close_matches(name, ENGLISH_BIBLE_BOOKS, n=1, cutoff=0.6)
    if en_match:
        return "EN", en_match[0]

    # ---------- Amharic ----------
    if name in AMHARIC_BOOKS:
        return "AM", name
    am_match = get_close_matches(name, AMHARIC_BOOKS, n=1, cutoff=0.5)
    if am_match:
        return "AM", am_match[0]

    return None, None

# ---------- Command Handler ----------
async def verse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Usage: /verse John 3:16 or /verse ዮሐንስ 3:16"""
    if not context.args:
        await update.message.reply_text("❌ Usage: /verse <Book> <Chapter>:<Verse>")
        return

    query = " ".join(context.args)

    match = re.match(r"(.+)\s+(\d+):(\d+)", query)
    if not match:
        await update.message.reply_text("❌ Invalid format. Example: /verse John 3:16")
        return

    book_name, chapter, verse = match.groups()
    chapter, verse = int(chapter), int(verse)

    lang, matched_book = find_book(book_name)
    if not matched_book:
        await update.message.reply_text(f"❌ Book not found: {book_name}")
        return

    # ---------- English API ----------
    if lang == "EN":
        try:
            response = requests.get(f"{BIBLE_API_URL}/{matched_book} {chapter}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                verses = data.get("verses", [])
                verse_text = next((v["text"] for v in verses if int(v["verse"]) == verse), None)
                if verse_text:
                    await update.message.reply_text(f"📖 {matched_book} {chapter}:{verse}\n\n{verse_text}")
                    return
        except:
            await update.message.reply_text("❌ Error fetching English verse from API.")
            return

    # ---------- Amharic Bible ----------
    if lang == "AM":
        chapters_list = bible_books_amharic[matched_book]
        chapter_obj = next((c for c in chapters_list if int(c["chapter"]) == chapter), None)
        if chapter_obj and 1 <= verse <= len(chapter_obj["verses"]):
            verse_text = chapter_obj["verses"][verse - 1].strip()
            await update.message.reply_text(f"📜 {matched_book} {chapter}:{verse}\n\n{verse_text}")
            return

    await update.message.reply_text("❌ Verse not found.")
