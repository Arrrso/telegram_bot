import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from contextlib import asynccontextmanager

# === Конфигурация ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен берём из переменных окружения
WEBHOOK_URL = os.getenv("WEBHOOK_URL")   # Например: https://your-app.onrender.com/webhook/<TOKEN>

if not TOKEN:
    raise ValueError("Не найден TELEGRAM_BOT_TOKEN в переменных окружения!")

application = Application.builder().token(TOKEN).build()

# === Хендлеры ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Я бот 🚀", reply_markup=reply_markup)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Ты сказал: {update.message.text}", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Возврат в начало 🔙", reply_markup=reply_markup)

# === Роутинг бота ===
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
application.add_handler(CallbackQueryHandler(button_handler))

# === FastAPI + Lifespan ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте
    await application.bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook установлен:", WEBHOOK_URL)
    yield
    # При завершении
    await application.bot.delete_webhook()
    print("🛑 Webhook удалён")

app = FastAPI(lifespan=lifespan)

# === Endpoint для Telegram ===
@app.post("/webhook/{token}")
async def webhook(request: Request, token: str):
    if token != TOKEN:
        return {"status": "forbidden"}  # Проверка безопасности

    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}
