import asyncio
import sqlite3
import qrcode
import cv2
import pandas as pd
from pyzbar import pyzbar
from datetime import datetime

from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8383578188:AAE6S_He8Jk_y72Kc60lSd3nVDMRFZNAuFQ"
ADMIN_ID = 697212400

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- DB ---
conn = sqlite3.connect("warehouse.db")
cursor = conn.cursor()

CATEGORIES = {
    "⚡ Електрика": ["Терморегулятор TC4L-14R", "Терморегулятор TC4S-14R", "Терморегулятор TC4W-14R",
                  "Потенціометр LPC PA010", "Теплове реле SM1P 0250", "Індуктивні датчики BRQM100-DDTA-P",
                  "Індуктивні датчики SA-CBM", "Пускач LC1E1210M5", "3-фазне реле PNPP-311M", "Реле (24B) R4N-2014-23-1024-WTL",
                  "Зумери червоні лампи AD22-22BM/r", "Інфра червоний датчик BJ30-BDT", "Регулятор холодильний 080G3457",
                  "Контактний блок start", "Контактний блок stop", "Кінцевик KB M1 S11", "Розетка 3-фази (16А)",
                  "Розетка 3-фази (32А)", "Вилка 3-фази (16А)", "Вилка 3-фази (32А)", "Блок живлення M-150-12V-12,5A",
                  "Повітряні тени", "Водяні тени", "Клювіки S2SRN-S3AW", "Аварійні лампи PTE-AGF-1FF-G (220B)",
                  "Аварійні лампи PTE-AGF-202-RG (24B)", "Кнопки start/stop S2TR-P3W", "Частотники ATV310HU22N4E", "Частотники ATV310HU15N4E"],
    "⚙️ Підшипники": ["6000", "6001", "6002", "6003", "6004", "6005", "6006", "6007", "6008", "6009",
               "6200", "6201", "6202", "6203", "6204", "6205", "6206", "6207", "6208", "6209", "6300",
               "6301", "6302", "6303", "6304", "6305", "6306", "6307", "6308", "6309"],
    "⚙️ Підшипники спец": ["2202-2rs", "uc204", "629z", "609-2z", "698z", "6902zz", "NA4903", "DF07R2ILA4", "E20 63803 2rs",
                   "606z", "695", "605", "6900", "30205/Q", "CSK17PP", "51309", "51204", "SA10-T/K", "51112", "53506H(22206CW33)", "UC208",
                   "LM 20UU", "LMEK 20UU", "6214", "W30V", "6210", "51211", "6212-2z", "3210-2rs", "53309U", "SIL12T/K"],
    "⭕ Сальники": ["17/47/7", "20/40/7", "20/47/7", "22/32/5", "22/40/7", "22/40/10", "25/37/7", "25/47/7", "28/40/7",
                 "28/40/8", "28/42/7", "28/52/7", "30/42/7", "30/45/7", "30/45/10", "30/47/7", "30/47/10", "30/50/7", "30/52/7", "30/55/7",
                 "30/62/10", "35/52/7", "35/55/7", "35/55/10", "35/62/10", "38/58/10", "40/50/7", "40/52/7", "40/55/10", "40/60/10",
                 "40/65/10", "40/68/7", "45/65/10", "45/72/10", "45/75/8", "50/65/8", "50/72/10", "55/65/8",
                 "58/80/10", "60/90/10"],
    "🔁 Стрічки Лінія №1": ["Відсадна машина нова", "Перехід стіл посипка", "Поворот стіл№1", "Поворот стіл№2", "Поворот стіл№3", "Перехід стіл перед декор", "Холодильний тунель", "Стіл збору печева"],
    "🔁 Стрічки Лінія №2": ["Ротоформовочна машина", "Поворотний стіл", "Стіл спуску", "Стіл стекера№1", "Стіл стекера№2", "Стіл стекера№3"],
    "🔁 Стрічки Лінія №3": ["HASBORG", "Стіл підйому", "Поворотний стіл№1", "Поворотний стіл№2", "Поворотний стіл№3", "Холодильний тунель№1", "Холодильний тунель№2(спуск)",
         "Холодильний тунель№3", "Холодильний тунель№4", "Стіл збору печева"],
    "🎗 Паси/Ремені": ["1760 BM", "28х8х800 Li", "360 5M", "385 5M", "520 5M", "3G910260", "41x13x1040 Li", "420 RPP5", "450 RPP5", "540L050", "645K6 6PK1640", "A-1018", "A-1080",
     "A-1400", "AVX 10x750 La", "AVX 10x900 La", "AVX 10x940 La", "AVX 13x850 La", "AVX 13x1050 La", "B-710", "B-750", "B-1060", "B-1700", "B-1860", "B-1900", "B-2000",
     "S5M 775", "S8M-1120", "SPA 932 Lw", "SPZ 912 Ld", "SPZ 1112", "SPZ 1462", "SPZ 1462 Lw", "SPZ 1800 Lw", "SPZ-1850", "SPZ/AV10-1280 Lp", "W40-1000 Lw", "XPN 1500",
     "XPZ-1850", "XPZ-1850-A", "Z 800 Lw", "Z-1100", "Z-1500", "ZR 169 L"],
    "⛓ Ланцюги": ["05В", "06В", "08В", "08В (дворядний)", "08В (поворотній)", "10В", "10В (дворядний)", "10В (поворотній)", "12В",
            "12В (дворядний)", "12В (поворотній)", "16В", "16В (дворядний)"],
    "⛓ Замки ланцюгів": ["Замок 05В", "Замок 06В", "Замок 08В", "Замок 08В (дворядний)", "Замок 08В (поворотній)", "Замок 10В", "Замок 10В (дворядний)", "Замок 10В (поворотній)", "Замок 12В", "Замок 12В (дворядний)", "Замок 12В (поворотній)", "Замок 16В", "Замок 16В (дворядний)"]
}
CATEGORY_LIST = list(CATEGORIES.keys())

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    role TEXT,
    status TEXT
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    quantity INTEGER,
    category TEXT
)
""")

def sync_items():
    for category, items in CATEGORIES.items():
        for item in items:
            cursor.execute("""
                           INSERT
                           OR IGNORE INTO items (name, quantity, category)
                VALUES (?, ?, ?)
                           """, (item, 1, category))

    conn.commit()

cursor.execute("SELECT COUNT(*) FROM items")
count = cursor.fetchone()[0]

if count == 0:
    for category, items in CATEGORIES.items():
        for item in items:
            cursor.execute(
                "INSERT OR IGNORE INTO items (name, quantity, category) VALUES (?, ?, ?)",
                (item, 1, category)
            )
    conn.commit()


cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    action TEXT,
    qty INTEGER,
    user_id INTEGER,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS boxes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS box_items (
    box_id INTEGER,
    item_id INTEGER
)
""")

conn.commit()


def fill_db_if_empty():
    # Перевіряємо, чи база вже не заповнена
    cursor.execute("SELECT COUNT(*) FROM items")
    count = cursor.fetchone()[0]  # [0] обов'язково, щоб отримати число

    if count == 0:
        print("Заповнюю базу даними зі списку CATEGORIES...")
        for category, items_list in CATEGORIES.items():
            for item_name in items_list:
                cursor.execute(
                    "INSERT INTO items (name, quantity, category) VALUES (?, ?, ?)",
                    (item_name, 0, category)  # Початкова кількість 0
                )
        conn.commit()
        print("Базу успішно заповнено!")


# Викликаємо функцію заповнення
sync_items()

# --- USERS ---
def get_role(uid):
    cursor.execute("SELECT role FROM users WHERE user_id=?", (uid,))
    r = cursor.fetchone()
    return r[0] if r else "user"

def add_user(uid, username):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, role, status) VALUES (?, ?, ?, ?)",
        (uid, username, "user", "pending")
    )
    conn.commit()

def is_approved(uid):
    cursor.execute("SELECT status FROM users WHERE user_id=?", (uid,))
    r = cursor.fetchone()
    return r and r[0] == "approved"

# --- KB ---
def main_kb(uid):
    kb = InlineKeyboardBuilder()
    kb.button(text="📦 Товари", callback_data="items")
    kb.button(text="🔍 Пошук", callback_data="search")

    if get_role(uid) == "admin":
        kb.button(text="👤 Адмінка", callback_data="admin")
        kb.button(text="📊 Експорт", callback_data="export")
        kb.button(text="📦 Boxes", callback_data="boxes")
        kb.button(text="⚠️ Дефіцит", callback_data="deficit")

    kb.adjust(1)
    return kb.as_markup()

def item_kb(item_id, is_admin, category):
    kb = InlineKeyboardBuilder()
    kb.button(text="➖", callback_data=f"dec_{item_id}")

    if is_admin:
        kb.button(text="❌ Видалити", callback_data=f"del_{item_id}")
        kb.button(text="➕", callback_data=f"inc_{item_id}")

        kb.button(text="+5", callback_data=f"inc5_{item_id}")
        kb.button(text="-5", callback_data=f"dec5_{item_id}")

        kb.button(text="🧾 QR", callback_data=f"qr_{item_id}")

    kb.button(
        text="⬅️ Назад",
        callback_data=f"cat_{category}_0"
    )

    kb.button(text="🏠 Меню", callback_data="menu")

    kb.adjust(2, 2, 1, 1)
    return kb.as_markup()


# --- START ---
@dp.message(Command("start"))
async def start(message: types.Message):
    uid = message.from_user.id

    add_user(uid, message.from_user.full_name)

    # ЖОРСТКО ставимо адміна
    if uid == ADMIN_ID:
        cursor.execute(
            "INSERT OR REPLACE INTO users (user_id, username, role, status) VALUES (?, ?, 'admin', 'approved')",
            (uid, message.from_user.full_name)
        )
        conn.commit()

    if not is_approved(uid) and uid != ADMIN_ID:
        await message.answer("⏳ Очікуйте підтвердження адміністратора")
        return

    await message.answer(
        "📦 Склад готовий до роботи",
        reply_markup=main_kb(message.from_user.id)
    )

# --- ADD ---
user_state = {}

@dp.callback_query(F.data == "stock")
async def show_stock(call: types.CallbackQuery):
    cursor.execute("SELECT name, quantity, category FROM items")
    items = cursor.fetchall()

    kb = InlineKeyboardBuilder()

    text = "📊 Залишки:\n\n"

    for i in items:
        text += f"{i[0]} — {i[1]} шт ({i[2]})\n"

    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)

    await call.message.edit_text(text, reply_markup=kb.as_markup())

PAGE_SIZE = 18

@dp.callback_query(F.data.startswith("cat_"))
async def open_category(call: types.CallbackQuery):
    parts = call.data.split("_")

    # ✅ Захист від кривих callback_data
    try:
        cat_id = int(parts[1])
    except:
        await call.answer("❌ Помилка категорії")
        return

    if cat_id < 0 or cat_id >= len(CATEGORY_LIST):
        await call.answer("❌ Некоректна категорія")
        return

    category = CATEGORY_LIST[cat_id]

    # ✅ Пагінація
    try:
        page = int(parts[2]) if len(parts) > 2 else 0
    except:
        page = 0

    # отримати кількість товарів
    cursor.execute(
        "SELECT COUNT(*) FROM items WHERE category=?",
        (category,)
    )
    total = cursor.fetchone()[0]

    offset = page * PAGE_SIZE

    cursor.execute(
        "SELECT id, name, quantity FROM items WHERE category=? LIMIT ? OFFSET ?",
        (category, PAGE_SIZE, offset)
    )
    items = cursor.fetchall()

    kb = InlineKeyboardBuilder()

    # товари
    for i in items:
        kb.button(
            text=f"{i[1]} ({i[2]})",
            callback_data=f"item_{i[0]}"
        )

    # навігація
    nav = []

    if page > 0:
        nav.append(
            types.InlineKeyboardButton(
                text="⬅️",
                callback_data=f"cat_{cat_id}_{page-1}"
            )
        )

    if (page + 1) * PAGE_SIZE < total:
        nav.append(
            types.InlineKeyboardButton(
                text="➡️",
                callback_data=f"cat_{cat_id}_{page+1}"
            )
        )

    if nav:
        kb.row(*nav)

    kb.row(
        types.InlineKeyboardButton(
            text="🏠 Меню",
            callback_data="menu"
        )
    )

    kb.adjust(1)

    await call.message.edit_text(
        f"📁 {category} (сторінка {page+1})",
        reply_markup=kb.as_markup()
    )

    await call.answer()


@dp.callback_query(F.data == "menu")
async def back_to_menu(call: types.CallbackQuery):
    try:
        await call.message.edit_text(
            "📦 Головне меню",
            reply_markup=main_kb(call.from_user.id)
        )
    except TelegramBadRequest:
        # Якщо повідомлення вже "Головне меню", Telegram видасть помилку.
        # Ми її ігноруємо, щоб бот не зупинявся.
        pass

    # Це прибере "годинничок" завантаження на кнопці
    await call.answer()

@dp.callback_query(F.data == "start")
async def start(call: types.CallbackQuery):
    await call.message.edit_text(
        "📦 Головне меню:",
        reply_markup=main_kb(call.from_user.id)
    )

@dp.callback_query(F.data == "add")
async def add(call: types.CallbackQuery):
    await call.message.answer("Назва:")
    user_state[call.from_user.id] = {}

@dp.message(F.text)
async def universal_input(message: types.Message):
    uid = message.from_user.id

    # --- ADD TO BOX ---
    if uid in add_box_state:
        box_id = add_box_state[uid]

        try:
            item_id = int(message.text)
        except:
            await message.answer("❌ Введи ID товару")
            return

        cursor.execute(
            "INSERT INTO box_items (box_id, item_id) VALUES (?, ?)",
            (box_id, item_id)
        )
        conn.commit()

        await message.answer("✅ Додано. Введи ще або натисни завершити")
        return

    # --- CREATE BOX ---
    if uid in box_state:
        cursor.execute("INSERT INTO boxes (name) VALUES (?)", (message.text,))
        conn.commit()

        del box_state[uid]

        await message.answer("✅ Box створено")
        return

    # --- SEARCH ---
    if uid in search_state:
        text = message.text

        cursor.execute(
            "SELECT id, name, quantity FROM items WHERE name LIKE ?",
            (f"%{text}%",)
        )
        results = cursor.fetchall()

        if not results:
            await message.answer("❌ Нічого не знайдено")
        else:
            kb = InlineKeyboardBuilder()

            for item in results:
                kb.button(
                    text=f"{item[1]} ({item[2]})",
                    callback_data=f"item_{item[0]}"
                )

            kb.adjust(1)

            await message.answer(
                "🔍 Результат пошуку:",
                reply_markup=kb.as_markup()
            )

        search_state.remove(uid)
        return

    # --- ADD ITEM ---
    if uid in user_state:
        if "name" not in user_state[uid]:
            user_state[uid]["name"] = message.text
            await message.answer("Кількість:")
        else:
            name = user_state[uid]["name"]
            qty = int(message.text)

            cursor.execute(
                "INSERT INTO items (name, quantity, category) VALUES (?, ?, ?)",
                (name, qty, "Без категорії")
            )
            conn.commit()

            await message.answer("✅ Додано")
            del user_state[uid]
        return

# --- ITEMS (PAGINATION) ---
@dp.callback_query(F.data == "items")
async def categories(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()

    for i, category in enumerate(CATEGORY_LIST):
        kb.button(text=category, callback_data=f"cat_{i}_0")

    kb.button(text="🏠 Меню", callback_data="menu")
    kb.adjust(1)

    await call.message.edit_text("📦 Категорії:", reply_markup=kb.as_markup())

# --- ITEM ---
@dp.callback_query(F.data.startswith("item_"))
async def item_view(call: types.CallbackQuery):
    item_id = int(call.data.split("_")[1])

    cursor.execute(
        "SELECT name, quantity, category FROM items WHERE id=?",
        (item_id,)
    )
    item = cursor.fetchone()

    if not item:
        await call.message.edit_text("❌ Товар не знайдено")
        await call.answer()
        return

    # 🔥 знаходимо ID категорії
    try:
        cat_id = CATEGORY_LIST.index(item[2])
    except ValueError:
        cat_id = 0  # fallback

    is_admin = get_role(call.from_user.id) == "admin"

    try:
        await call.message.edit_text(
            f"{item[0]}\nКількість: {item[1]}",
            reply_markup=item_kb(item_id, is_admin, cat_id)
        )
    except TelegramBadRequest:
        await call.message.answer(
            f"{item[0]}\nКількість: {item[1]}",
            reply_markup=item_kb(item_id, is_admin, cat_id)
        )

    await call.answer()
# --- LOG ---
def log(item_id, action, qty, user_id):
    cursor.execute(
        "INSERT INTO logs (item_id, action, qty, user_id, date) VALUES (?,?,?,?,?)",
        (item_id, action, qty, user_id, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()

# --- INC/DEC ---
@dp.callback_query(F.data.startswith("inc_"))
async def inc(call: types.CallbackQuery):
    item_id = int(call.data.split("_")[1])
    cursor.execute("UPDATE items SET quantity=quantity+1 WHERE id=?", (item_id,))
    conn.commit()
    log(item_id, "add", 1, call.from_user.id)
    await item_view(call)

@dp.callback_query(F.data.startswith("dec_"))
async def dec(call: types.CallbackQuery):
    item_id = int(call.data.split("_")[1])
    cursor.execute("UPDATE items SET quantity=quantity-1 WHERE id=?", (item_id,))
    conn.commit()
    log(item_id, "remove", 1, call.from_user.id)
    await item_view(call)

@dp.callback_query(F.data.startswith("inc5_"))
async def inc5(call: types.CallbackQuery):
    item_id = int(call.data.split("_")[1])

    cursor.execute("UPDATE items SET quantity=quantity+5 WHERE id=?", (item_id,))
    conn.commit()

    log(item_id, "add", 5, call.from_user.id)

    await item_view(call)

@dp.callback_query(F.data.startswith("dec5_"))
async def dec5(call: types.CallbackQuery):
    item_id = int(call.data.split("_")[1])

    cursor.execute("SELECT quantity FROM items WHERE id=?", (item_id,))
    qty = cursor.fetchone()[0]

    if qty < 5:
        await call.answer("❌ Недостатньо товару")
        return

    cursor.execute("UPDATE items SET quantity=quantity-5 WHERE id=?", (item_id,))
    conn.commit()

    log(item_id, "remove", 5, call.from_user.id)

    await item_view(call)

# --- DELETE ---
@dp.callback_query(F.data.startswith("del_"))
async def delete(call: types.CallbackQuery):
    item_id = int(call.data.split("_")[1])
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    await call.answer("✅ Видалено")
    await call.message.edit_text("❌ Видалено", reply_markup=main_kb(call.from_user.id))

# --- QR ---
@dp.callback_query(F.data.regexp(r"^qr_\d+$"))
async def qr(call: types.CallbackQuery):
    data = call.data.split("_")

    # 🔥 фільтр — щоб не лізли qr_box
    if data[1] == "box":
        return

    item_id = int(data[1])

    img = qrcode.make(f"item_{item_id}")
    img.save("qr.png")

    await call.message.answer_photo(FSInputFile("qr.png"))

# --- SCAN ---
@dp.message(F.photo)
async def scan(message: types.Message):
    file = await bot.get_file(message.photo[-1].file_id)
    await bot.download_file(file.file_path, "scan.jpg")

    img = cv2.imread("scan.jpg")
    decoded = pyzbar.decode(img)

    if not decoded:
        await message.answer("❌ QR не знайдено")
        return

    data = decoded[0].data.decode()

    if data.startswith("box_"):
        box_id = int(data.split("_")[1])
        await open_box_by_id(message, box_id)
        return

    if data.startswith("item_"):
        item_id = int(data.split("_")[1])

        cursor.execute("SELECT name, quantity FROM items WHERE id=?", (item_id,))
        item = cursor.fetchone()

        if item:
            await message.answer(f"{item[0]} — {item[1]} шт")

# --- SEARCH ---
search_state = set()

@dp.callback_query(F.data == "search")
async def search(call: types.CallbackQuery):
    search_state.add(call.from_user.id)
    await call.message.answer("Введи назву:")

@dp.callback_query(F.data.startswith("deficit"))
async def deficit(call: types.CallbackQuery):
    parts = call.data.split("_")
    page = int(parts[1]) if len(parts) > 1 else 0

    LIMIT = 20
    offset = page * LIMIT

    cursor.execute(
        "SELECT COUNT(*) FROM items WHERE quantity <= 5"
    )
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT name, quantity FROM items WHERE quantity <= 5 ORDER BY quantity ASC LIMIT ? OFFSET ?",
        (LIMIT, offset)
    )
    items = cursor.fetchall()

    if not items:
        await call.message.edit_text("✅ Немає дефіцитних товарів")
        return

    text = f"⚠️ Дефіцит (сторінка {page+1}):\n\n"

    for item in items:
        text += f"{item[0]} — {item[1]} шт\n"

    kb = InlineKeyboardBuilder()

    # ⬅️➡️
    nav = []

    if page > 0:
        nav.append(
            types.InlineKeyboardButton(
                text="⬅️",
                callback_data=f"deficit_{page-1}"
            )
        )

    if (page + 1) * LIMIT < total:
        nav.append(
            types.InlineKeyboardButton(
                text="➡️",
                callback_data=f"deficit_{page+1}"
            )
        )

    if nav:
        kb.row(*nav)

    kb.button(text="🏠 Меню", callback_data="menu")
    kb.adjust(1)

    if len(text) > 3500:
        text = text[:3500] + "\n\n... (обрізано)"

    await call.message.edit_text(text, reply_markup=kb.as_markup())


# --- ADMIN ---
@dp.callback_query(F.data == "admin")
async def admin(call: types.CallbackQuery):
    cursor.execute("""
                   SELECT user_id, username, status, role
                   FROM users
                   """)
    users = cursor.fetchall()

    kb = InlineKeyboardBuilder()

    if not users:
        await call.message.edit_text("✅ Немає заявок на підтвердження")
        return

    for u in users:
        kb.button(
            text=f"{u[1]} | {u[3]} | {u[2]}",
            callback_data=f"user_{u[0]}"
        )

    kb.button(text="⬅️ Назад", callback_data="menu")
    kb.adjust(1)

    await call.message.edit_text("⏳ Очікують підтвердження:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("user_"))
async def user_manage(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])

    cursor.execute("SELECT username, status FROM users WHERE user_id=?", (uid,))
    user = cursor.fetchone()

    if not user:
        await call.answer("❌ Користувача не знайдено")
        return

    kb = InlineKeyboardBuilder()

    kb.button(text="✅ Підтвердити", callback_data=f"approve_{uid}")
    kb.button(text="❌ Відхилити", callback_data=f"reject_{uid}")
    kb.button(text="👑 Зробити адміном", callback_data=f"makeadmin_{uid}")
    kb.button(text="🧍 Зняти адмінку", callback_data=f"removeadmin_{uid}")
    kb.button(text="⬅️ Назад", callback_data="admin")
    kb.button(text="🏠 Меню", callback_data="menu")

    kb.adjust(1)

    await call.message.edit_text(
        f"👤 {user[0]}\nСтатус: {user[1]}\nID: {uid}",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("makeadmin_"))
async def make_admin(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    cursor.execute("UPDATE users SET role='admin' WHERE user_id=?", (uid,))
    conn.commit()
    await call.answer("OK")

@dp.callback_query(F.data.startswith("removeadmin_"))
async def remove_admin(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])
    cursor.execute("UPDATE users SET role='user' WHERE user_id=?", (uid,))
    conn.commit()
    await call.answer("OK")

@dp.callback_query(F.data.startswith("approve_"))
async def approve(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])

    cursor.execute("UPDATE users SET status='approved' WHERE user_id=?", (uid,))
    conn.commit()

    await call.answer("✅ Підтверджено")


@dp.callback_query(F.data.startswith("reject_"))
async def reject(call: types.CallbackQuery):
    uid = int(call.data.split("_")[1])

    cursor.execute("DELETE FROM users WHERE user_id=?", (uid,))
    conn.commit()

    await call.answer("❌ Відхилено")

# --- EXPORT ---
@dp.callback_query(F.data == "export")
async def export(call: types.CallbackQuery):
    df = pd.read_sql_query("SELECT * FROM items", conn)
    df.to_csv("items.csv", index=False)
    await call.message.answer_document(FSInputFile("items.csv"))

# --- RUN ---
# === MINI WMS: BOX SYSTEM (з ➕➖ прямо в списку) ===

# --- DB ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS boxes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS box_items (
    box_id INTEGER,
    item_id INTEGER
)
""")

conn.commit()

# --- BOX MENU ---
@dp.callback_query(F.data == "boxes")
async def boxes_menu(call: types.CallbackQuery):
    cursor.execute("SELECT id, name FROM boxes")
    boxes = cursor.fetchall()

    kb = InlineKeyboardBuilder()

    for b in boxes:
        kb.button(text=f"📦 {b[1]}", callback_data=f"box_{b[0]}")

    kb.button(text="➕ Створити box", callback_data="create_box")
    kb.button(text="⬅️ Назад", callback_data="menu")

    kb.adjust(1)

    await call.message.edit_text("📦 Коробки:", reply_markup=kb.as_markup())

# --- CREATE BOX ---
box_state = {}

@dp.callback_query(F.data == "create_box")
async def create_box(call: types.CallbackQuery):
    box_state[call.from_user.id] = True
    await call.message.answer("Введи назву коробки:")


# --- OPEN BOX ---
@dp.callback_query(F.data.startswith("box_"))
async def open_box(call: types.CallbackQuery):
    box_id = int(call.data.split("_")[1])

    cursor.execute("SELECT name FROM boxes WHERE id=?", (box_id,))
    box = cursor.fetchone()

    if not box:
        await call.answer("❌ Box не знайдено")
        return

    cursor.execute("""
        SELECT items.id, items.name, items.quantity
        FROM box_items
        JOIN items ON items.id = box_items.item_id
        WHERE box_items.box_id=?
    """, (box_id,))

    items = cursor.fetchall()

    kb = InlineKeyboardBuilder()

    text = f"📦 {box[0]}\n\n"

    for item in items:
        text += f"{item[1]} — {item[2]} шт\n"

    kb.button(text="➕ Додати товар", callback_data=f"add_to_box_{box_id}_0")
    kb.button(text="🧾 QR", callback_data=f"qr_box_{box_id}")
    kb.button(text="⬅️ Назад", callback_data="boxes")

    kb.adjust(1)

    await call.message.edit_text(text, reply_markup=kb.as_markup())

# --- ➕➖ ОБРОБНИКИ ---
@dp.callback_query(F.data.startswith("boxinc_"))
async def box_inc(call: types.CallbackQuery):
    _, item_id, box_id = call.data.split("_")

    cursor.execute("UPDATE items SET quantity=quantity+1 WHERE id=?", (item_id,))
    conn.commit()

    await open_box(call)

@dp.callback_query(F.data.startswith("boxdec_"))
async def box_dec(call: types.CallbackQuery):
    _, item_id, box_id = call.data.split("_")

    cursor.execute("SELECT quantity FROM items WHERE id=?", (item_id,))
    qty = cursor.fetchone()[0]

    if qty <= 0:
        await call.answer("❌ Немає в наявності")
        return

    cursor.execute("UPDATE items SET quantity=quantity-1 WHERE id=?", (item_id,))
    conn.commit()

    await open_box(call)

# --- ADD ITEM TO BOX ---
add_box_state = {}

@dp.callback_query(F.data.startswith("add_to_box_"))
async def add_to_box(call: types.CallbackQuery):
    parts = call.data.split("_")

    box_id = int(parts[3])
    page = int(parts[4]) if len(parts) > 4 else 0

    add_box_state[call.from_user.id] = box_id

    PAGE_SIZE = 10
    offset = page * PAGE_SIZE

    cursor.execute(
        "SELECT id, name FROM items LIMIT ? OFFSET ?",
        (PAGE_SIZE, offset)
    )
    items = cursor.fetchall()

    kb = InlineKeyboardBuilder()

    for i in items:
        kb.button(text=i[1], callback_data=f"additem_{i[0]}")

    # 🔥 навігація
    nav = []

    if page > 0:
        nav.append(
            types.InlineKeyboardButton(
                text="⬅️",
                callback_data=f"add_to_box_{box_id}_{page-1}"
            )
        )

    cursor.execute("SELECT COUNT(*) FROM items")
    total = cursor.fetchone()[0]

    if (page + 1) * PAGE_SIZE < total:
        nav.append(
            types.InlineKeyboardButton(
                text="➡️",
                callback_data=f"add_to_box_{box_id}_{page+1}"
            )
        )

    if nav:
        kb.row(*nav)

    kb.button(text="⬅️ Завершити", callback_data="finish_add")

    kb.adjust(1)

    await call.message.edit_text(
        f"📦 Вибери товар (сторінка {page+1})",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data.startswith("additem_"))
async def add_item_to_box(call: types.CallbackQuery):
    uid = call.from_user.id
    item_id = int(call.data.split("_")[1])

    if uid not in add_box_state:
        await call.answer("❌ Не активний режим")
        return

    box_id = add_box_state[uid]

    cursor.execute(
        "INSERT INTO box_items (box_id, item_id) VALUES (?, ?)",
        (box_id, item_id)
    )
    conn.commit()

    await call.answer("✅ Додано")

@dp.callback_query(F.data == "finish_add")
async def finish_add(call: types.CallbackQuery):
    uid = call.from_user.id

    if uid in add_box_state:
        del add_box_state[uid]

    try:
        await call.message.edit_text(
            "📦 Головне меню:",
            reply_markup=main_kb(uid)
        )
    except:
        await call.message.answer(
            "📦 Головне меню:",
            reply_markup=main_kb(uid)
        )

    await call.answer()



# --- QR BOX ---
@dp.callback_query(F.data.startswith("qr_box_"))
async def qr_box(call: types.CallbackQuery):
    box_id = int(call.data.split("_")[2])

    img = qrcode.make(f"box_{box_id}")
    img.save("box.png")

    await call.message.answer_photo(FSInputFile("box.png"))

# --- SCAN BOX ---
async def open_box_by_id(message, box_id):
    cursor.execute("SELECT name FROM boxes WHERE id=?", (box_id,))
    box = cursor.fetchone()

    if not box:
        await message.answer("❌ Box не знайдено")
        return

    cursor.execute("""
        SELECT items.id, items.name, items.quantity
        FROM box_items
        JOIN items ON items.id = box_items.item_id
        WHERE box_items.box_id=?
    """, (box_id,))

    items = cursor.fetchall()

    kb = InlineKeyboardBuilder()

    text = f"📦 {box[0]}\n\n"

    for item in items:
        text += f"{item[1]} — {item[2]} шт\n"

    kb.button(text="⬅️ Назад", callback_data="boxes")
    kb.adjust(1)

    await message.answer(text, reply_markup=kb.as_markup())

# --- MAIN MENU BUTTON ---
# kb.button(text="📦 Boxes", callback_data="boxes")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
