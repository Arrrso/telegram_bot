"""
bot.py

Файл: бот Telegram на python-telegram-bot (v20+) с поддержкой .env (python-dotenv).

Инструкция по использованию (кратко):
1) Создайте файл .env в той же папке, где bot.py, и поместите туда:

    BOT_TOKEN=ВАШ_ТОКЕН_ЗДЕСЬ

2) Установите зависимости (рекомендуется в virtualenv):

    python -m venv venv
    # Windows
    .\venv\Scripts\Activate
    # macOS / Linux
    source venv/bin/activate

    python -m pip install --upgrade pip
    pip install python-telegram-bot python-dotenv

3) Запустите бота:

    python bot.py

4) НЕ ЗАБУДЬТЕ: .env не должен попадать в git. Добавьте в .gitignore строку:

    .env

Если ваш токен был случайно опубликован — зайдите в @BotFather и перегенерируйте (revoke) токен.

"""

import os
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Загрузим .env (если есть)
load_dotenv()

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

# Числа от 10 до 30 включительно
numbers = list(range(10, 31))


# --- Вспомогательные функции ---
def generate_trip(chosen_vokzal: str | None = None) -> str:
    """Сгенерировать текст поездки. Если chosen_vokzal указан, используем его."""
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
        "<b>Привет!</b>\nНажми кнопку, чтобы сгенерировать маршрут или выбрать вокзал.",
        reply_markup=reply_markup
    )


async def trip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /trip — просто отправляет случайный маршрут"""
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
        # покажем кнопки с вокзалами (несколько в ряд)
        keyboard = []
        row = []
        for i, v in enumerate(vokzals.keys(), start=1):
            row.append(InlineKeyboardButton(v, callback_data=f"vokzal:{v}"))
            # 3 кнопки в ряд
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
        # вернёмся в главное меню
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
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("Ошибка: не найден BOT_TOKEN. Установите токен в .env или в переменной окружения.")
        return

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trip", trip_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Бот запущен через polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
