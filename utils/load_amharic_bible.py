import os
import json

def load_amharic_bible():
    AMH_BIBLE_PATH = "amharic_bible"  # folder with JSON books
    bible_books = {}

    # Load all JSON books dynamically
    for file_name in os.listdir(AMH_BIBLE_PATH):
        if file_name.endswith(".json"):
            file_path = os.path.join(AMH_BIBLE_PATH, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Remove number prefix and .json extension
                book_name = "_".join(file_name.split("_")[1:]).replace(".json", "").strip()
                bible_books[book_name] = data["chapters"]

    print(f"✅ Loaded {len(bible_books)} Amharic books.")
    return bible_books
