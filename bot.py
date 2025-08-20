"""
bot.py (для Render, 24/7)
"""

import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# --- Данные вокзалов и направлений ---
vokzals = {
    "Белорусский": ["Одинцово", "Кубинка", "Звенигород", "Трехгорка", "Голицыно", "Тучково", "Можайск", "Сетунь"],
    "Казанский":   ["Голутвин", "Люберцы", "Раменское", "Шатура"],
    "Киевский":    ["Переделкино", "Очаково", "Нара", "Балабаново", "Обнинск", "Лесной городок", "Малоярославец"],
    "Курский":     ["Переделкино", "Очаково", "Нара", "Балабаново", "Обнинск", "Лесной городок", "Малоярославец"],
    "Ленинградский":["Крюково", "Химки", "Клин", "Сходня", "Подсолнечная", "Ховрино"],
    "Павелецкий":  ["Ступино", "Бирюлево", "Расторгуево", "Кашира", "Узуново", "Барыбино"],
    "Рижский":      ["Волоколамск", "Нахабино", "Истра", "Новоиерусалимская", "Румянцево"],
    "Савеловский": ["Лобня", "Дмитров", "Долгопрудная", "Дубна", "Большая Волга", "Бескудниково", "Водники", "Катуар"],
    "Ярославский":  ["Сергиев Посад", "Пушкино", "Монино", "Александров", "Фрязино", "Болшево", "Мытищи"]
}

numbers = list(range(10, 31))

# --- Вспомогательные функции ---
def generate_trip(chosen_vokzal: str | None = None) -> str:
    if chosen_vokzal and chosen_vokzal in vokzals:
        vokzal = chosen_vokzal
    else:
        vokzal = random.choice(list(vokzals.keys()))

    direction = random.choice(vokzals[vokzal])
    station_number = random.choice(numbers)

    text = (
        f"Ваш вокзал: <b>{vokzal}</b>\n"
        f"Направление: Москва — <b>{direction}</b>\n"
        f"Станция для выхода: <b>{station_number}</b>\n\n"
        "Приятного путешествия! 🚆"
    )
    return text

# --- Хендлеры ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Рандомное приключение", callback_data="random")],
        [InlineKeyboardButton("📍 Выбрать вокзал", callback_data="choose")],
        [InlineKeyboardButton("📌 Список вокзалов", callback_data="list")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        "👋 Привет!\nЯ помогу тебе выбрать вокзал, направление и случайную станцию для выхода.\nНажми кнопку — и узнаешь, откуда и куда поедешь 🚆✨",
        reply_markup=reply_markup
    )

async def trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = generate_trip()
    await update.message.reply_html(text)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
        await query.edit_message_text("Выберите вокзал:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("vokzal:"):
        vokzal_name = data.split(":", 1)[1]
        text = generate_trip(chosen_vokzal=vokzal_name)
        await query.edit_message_text(text, parse_mode="HTML")
    elif data == "back":
        await query.edit_message_text(
            "Главное меню:\nНажмите кнопку, чтобы сгенерировать маршрут или выбрать вокзал.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎲 Рандомное приключение", callback_data="random")],
                [InlineKeyboardButton("📍 Выбрать вокзал", callback_data="choose")],
                [InlineKeyboardButton("📌 Список вокзалов", callback_data="list")],
            ])
        )

# --- Запуск приложения ---

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("Ошибка: не найден BOT_TOKEN. Установите переменную окружения на Render.")
        return

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trip", trip_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущен через polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
