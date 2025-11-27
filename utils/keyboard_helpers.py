from telegram import ReplyKeyboardMarkup

def generate_buttons(items, page=0, page_size=20, columns=4, include_back=True):
   
    start = page * page_size
    end = start + page_size
    page_items = items[start:end]

    # Split items into rows with "columns" buttons each
    keyboard = [page_items[i:i+columns] for i in range(0, len(page_items), columns)]

    # Pagination buttons
    pagination_row = []
    if start > 0:
        pagination_row.append("Prev")
    if end < len(items):
        pagination_row.append("Next")
    if pagination_row:
        keyboard.append(pagination_row)

    # Back button
    if include_back:
        keyboard.append(["⬅️ Back"])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
