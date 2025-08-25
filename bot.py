
import os
import random
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

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

numbers = [10]*5 + [11]*10 + [12]*10 + [13]*10 + [14]*10 + [15]*10 + [16]*10 + [17]*10 + [18]*10 + [19]*10 + [20]*10 + [21]*10 + [22]*10 + [23]*5 + [24]*5 + [25]*7 + [26]*7 + [27]*7 + [28]*7 + [29]*7 + [30]*7

def generate_trip(chosen_vokzal: str | None = None) -> str:
    vokzal = chosen_vokzal if chosen_vokzal in vokzals else random.choice(list(vokzals.keys()))
    direction = random.choice(vokzals[vokzal])
    station_number = random.choice(numbers)
    return f"Ваш вокзал: <b>{vokzal}</b>\nНаправление: Москва — <b>{direction}</b>\nСтанция для выхода: <b>{station_number}</b>\n\nПриятного путешествия! 🚆"

fastapi_app = FastAPI()
TOKEN = os.environ.get("BOT_TOKEN")
bot = Bot(TOKEN)
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Рандомное приключение", callback_data="random")],
        [InlineKeyboardButton("📍 Выбрать вокзал", callback_data="choose")],
        [InlineKeyboardButton("📌 Список вокзалов", callback_data="list")],
    ]
    await update.message.reply_html(
        "👋 Привет! Я помогу тебе выбрать вокзал, направление и случайную станцию для выхода.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back")]])

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "random":
        text = generate_trip()
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_button())
    elif data == "list":
        vokzal_list = "\n".join(f"• {v}" for v in vokzals.keys())
        await query.edit_message_text(f"<b>Список вокзалов:</b>\n{vokzal_list}", parse_mode="HTML", reply_markup=back_button())
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
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=back_button())
    elif data == "back":
        await query.edit_message_text(
            "Главное меню:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎲 Рандомное приключение", callback_data="random")],
                [InlineKeyboardButton("📍 Выбрать вокзал", callback_data="choose")],
                [InlineKeyboardButton("📌 Список вокзалов", callback_data="list")],
            ])
        )

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

@fastapi_app.post("/webhook/{token}")
async def webhook(token: str, request: Request):
    if token != TOKEN:
        return {"status": "unauthorized"}
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}
