# bot.py
import os
import random
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

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

# --- Числа с весами ---
numbers = [10]*2 + [11]*3 + [12]*3 + [13]*3 + [14]*3 + \
          [15]*4 + [16]*4 + [17]*4 + [18]*4 + [19]*4 + [20]*4 + \
          [21]*3 + [22]*3 + [23]*2 + [24]*3 + [25]*2 + [26]*2 + [27]*1 + [28]*1 + [29]*1 + [30]*1

def generate_trip(chosen_vokzal=None):
    vokzal = chosen_vokzal if chosen_vokzal in vokzals else random.choice(list(vokzals.keys()))
    direction = random.choice(vokzals[vokzal])
    station_number = random.choice(numbers)
    text = (
        f"Ваш вокзал: <b>{vokzal}</b>\n"
        f"Направление: Москва — <b>{direction}</b>\n"
        f"Станция для выхода: <b>{station_number}</b>\n\n"
        "Приятного путешествия! 🚆"
    )
    return text

# --- Создаём FastAPI приложение ---
fastapi_app = FastAPI()
application = Application.builder().token(TOKEN).build()
application.initialize()  # важно!

@fastapi_app.post(f"/webhook/{TOKEN}")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, Bot(TOKEN))
    await application.process_update(update)
    return {"ok": True}

# --- Регистрируем команды и кнопки ---
async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🎲 Рандомное приключение", callback_data="random")],
        [InlineKeyboardButton("📍 Выбрать вокзал", callback_data="choose")],
        [InlineKeyboardButton("📌 Список вокзалов", callback_data="list")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(
        "👋 Привет!\nЯ помогу тебе выбрать вокзал, направление и случайную станцию для выхода.\nНажми кнопку — и узнаешь, откуда и куда поедешь 🚆✨",
        reply_markup=reply_markup
    )

async def trip_command(update, context):
    await update.message.reply_html(generate_trip())

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "random":
        text = generate_trip()
        await query.edit_message_text(text, parse_mode="HTML")
    elif data == "list":
        vokzal_list = "\n".join(f"• {v}" for v in vokzals.keys())
        await query.edit_message_text(f"<b>Список вокзалов:</b>\n{vokzal_list}", parse_mode="HTML")
    elif data == "choose":
        keyboard = []
        row = []
        for i, v in enumerate(vokzals.keys(), start=1):
            row.append(InlineKeyboardButton(v, callback_data=f"vokzal:{v}"))
            if i % 3 == 0:
                keyboard.append(row)
                row = []
        if row: keyboard.append(row)
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
        await query.edit_message_text("Выберите вокзал:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("vokzal:"):
        vokzal_name = data.split(":",1)[1]
        await query.edit_message_text(generate_trip(vokzal_name), parse_mode="HTML")
    elif data == "back":
        keyboard = [
            [InlineKeyboardButton("🎲 Рандомное приключение", callback_data="random")],
            [InlineKeyboardButton("📍 Выбрать вокзал", callback_data="choose")],
            [InlineKeyboardButton("📌 Список вокзалов", callback_data="list")]
        ]
        await query.edit_message_text(
            "Главное меню:\nНажмите кнопку, чтобы сгенерировать маршрут или выбрать вокзал.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# --- Добавляем хендлеры ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("trip", trip_command))
application.add_handler(CallbackQueryHandler(button_handler))
