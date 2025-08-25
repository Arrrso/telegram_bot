# bot.py для Render + webhook, Telegram Bot API v20+
import os
import random
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
WEBHOOK_PATH = f"/webhook/{TOKEN}"  # endpoint для webhook

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

# --- Числа с разной вероятностью ---
numbers = [10]*1 + [11,12,13,14]*3 + list(range(15,24))*6 + list(range(24,31))*4

# --- Вспомогательная функция генерации маршрута ---
def generate_trip(chosen_vokzal: str | None = None) -> str:
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

# --- Создаем приложение Telegram ---
application = Application.builder().token(TOKEN).build()

# --- Хендлеры ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Рандомное приключение", callback_data="random")],
        [InlineKeyboardButton("📍 Выбрать вокзал", callback_data="choose")],
        [InlineKeyboardButton("📌 Список вокзалов", callback_data="list")]
    ]
    await update.message.reply_html(
        "👋 Привет!\nЯ помогу тебе выбрать вокзал, направление и случайную станцию для выхода.\nНажми кнопку — и узнаешь маршрут 🚆✨",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "random":
        text = generate_trip()
    elif data == "list":
        text = "<b>Список вокзалов:</b>\n" + "\n".join(f"• {v}" for v in vokzals.keys())
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
        return
    elif data.startswith("vokzal:"):
        vokzal_name = data.split(":",1)[1]
        text = generate_trip(chosen_vokzal=vokzal_name)
    elif data == "back":
        text = "Главное меню:\nНажмите кнопку, чтобы сгенерировать маршрут или выбрать вокзал."
    else:
        text = "Непонятная команда."

    # Кнопка "Назад" после действия
    keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back")]]
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

# --- FastAPI ---
fastapi_app = FastAPI()

@fastapi_app.on_event("startup")
async def on_startup():
    # Устанавливаем webhook при старте
    await application.initialize()
    webhook_url = os.environ.get("WEBHOOK_URL")
    if webhook_url:
        await application.bot.set_webhook(webhook_url)
        print(f"Webhook установлен: {webhook_url}")

@fastapi_app.on_event("shutdown")
async def on_shutdown():
    await application.shutdown()

@fastapi_app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    update = Update.de_json(await request.json(), application.bot)
    await application.process_update(update)
    return {"ok": True}

# --- Для локального теста ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
