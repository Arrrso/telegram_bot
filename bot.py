import os
import random
import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# --- Создаём FastAPI ---
app = FastAPI()

# --- Создаём бота ---
application = Application.builder().token(TOKEN).build()

# --- Хэндлеры ---
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Сгенерировать число", callback_data="random")]
    ]
    await update.message.reply_text(
        "Привет! Я бот, который генерирует случайное число 🚂",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def button(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "random":
        number = weighted_random_number()
        keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
        await query.edit_message_text(
            text=f"🎲 Ваше число: {number}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("Сгенерировать число", callback_data="random")]
        ]
        await query.edit_message_text(
            text="Привет! Я бот, который генерирует случайное число 🚂",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

def weighted_random_number():
    # 14–24 чаще, 10–14 редко, 24–30 средне
    weights = []
    for i in range(10, 31):
        if 14 <= i <= 24:
            weights.append(6)
        elif 10 <= i < 14:
            weights.append(1)
        else:  # 25–30
            weights.append(3)
    return random.choices(range(10, 31), weights=weights, k=1)[0]

# --- Добавляем хэндлеры ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

# --- Роуты для Render ---
@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.start()
    # Устанавливаем webhook
    url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook/{TOKEN}"
    await application.bot.set_webhook(url)

@app.post("/webhook/{token}")
async def webhook(token: str, request: Request):
    if token != TOKEN:
        return {"error": "invalid token"}
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}
