import os

AMH_BIBLE_PATH = "amharic_bible"

for file_name in os.listdir(AMH_BIBLE_PATH):
    if file_name.endswith(".json"):
        print(file_name)
