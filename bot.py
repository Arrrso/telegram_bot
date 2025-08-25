import os
import random
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from contextlib import asynccontextmanager

# === Конфигурация ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN or not WEBHOOK_URL:
    raise ValueError("Необходимо указать TELEGRAM_BOT_TOKEN и WEBHOOK_URL в переменных окружения!")

# --- Данные вокзалов и направлений ---
vokzals = {
    "Белорусский": ["Одинцово", "Кубинка", "Звенигород", "Трехгорка", "Голицыно", "Тучково", "Можайск", "Сетунь"],
    "Казанский": ["Голутвин", "Люберцы", "Раменское", "Шатура"],
    "Киевский": ["Переделкино", "Очаково", "Нара", "Балабаново", "Обнинск", "Лесной городок", "Малоярославец"],
    "Курский": ["Переделкино", "Очаково", "Нара", "Балабаново", "Обнинск", "Лесной городок", "Малоярославец"],
    "Ленинградский": ["Крюково", "Химки", "Клин", "Сходня", "Подсолнечная", "Ховрино"],
    "Павелецкий": ["Ступино", "Бирюлево", "Расторгуево", "Кашира", "Узуново", "Барыбино"],
    "Рижский": ["Волоколамск", "Нахабино", "Истра", "Новоиерусалимская", "Румянцево"],
    "Савеловский": ["Лобня", "Дмитров", "Долгопрудная", "Дубна", "Большая Волга", "Бескудниково", "Водники", "Катуар"],
    "Ярославский": ["Сергиев Посад", "Пушкино", "Монино", "Александров", "Фрязино", "Болшево", "Мытищи"]
}

# --- Генерация номера станции (14-24 чаще, 10-14 редко, 25-30 средне) ---
def weighted_random_number():
    weights = []
    for i in range(10, 31):
        if 14 <= i <= 24:
            weights.append(6)
        elif 10 <= i < 14:
            weights.append(1)
        else:
            weights.append(3)
    return random.choices(range(10, 31), weights=weights, k=1)[0]

# --- Генерация маршрута ---
def generate_trip(chosen_vokzal: str | None = None) -> str:
    if chosen_vokzal and chosen_vokzal in vokzals:
        vokzal = chosen_vokzal
    else:
        vokzal = random.choice(list(vokzals.keys()))

    direction = random.choice(vokzals[vokzal])
    station_number = weighted_random_number()

    return (
        f"Ваш вокзал: <b>{vokzal}</b>\n"
        f"Направление: Москва — <b>{direction}</b>\n"
        f"Станция для выхода: <b>{station_number}</b>\n\n"
        "Приятного путешествия! 🚆"
    )

# --- Создаём приложение бота ---
application = Application.builder().token(TOKEN).build()

# --- Хендлеры ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Рандомное приключение", callback_data="random")],
        [InlineKeyboardButton("📍 Выбрать вокзал", callback_data="choose")],
        [InlineKeyboardButton("📌 Список вокзалов", callback_data="list")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(
        "👋 Привет!\nЯ помогу тебе выбрать вокзал, направление и случайную станцию для выхода.",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "random":
        text = generate_trip()
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "list":
        vokzal_list = "\n".join(f"• {v}" for v in vokzals.keys())
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
        await query.edit_message_text(f"<b>Список вокзалов:</b>\n{vokzal_list}", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "choose":
        keyboard = []
        row = []
        for i, v in enumerate(vokzals.keys(), start=1):
            row.append(InlineKeyboardButton(v, callback_data=f"vokzal:{v}"))
            if i % 3 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
        await query.edit_message_text("Выберите вокзал:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("vokzal:"):
        vokzal_name = data.split(":", 1)[1]
        text = generate_trip(chosen_vokzal=vokzal_name)
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("🎲 Рандомное приключение", callback_data="random")],
            [InlineKeyboardButton("📍 Выбрать вокзал", callback_data="choose")],
            [InlineKeyboardButton("📌 Список вокзалов", callback_data="list")],
        ]
        await query.edit_message_text(
            "Главное меню:\nНажмите кнопку, чтобы сгенерировать маршрут или выбрать вокзал.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# --- FastAPI + Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    await application.bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook установлен:", WEBHOOK_URL)
    yield
    await application.bot.delete_webhook()
    print("🛑 Webhook удалён")

app = FastAPI(lifespan=lifespan)

@app.post("/webhook/{token}")
async def webhook(token: str, request: Request):
    if token != TOKEN:
        return {"status": "forbidden"}
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}
