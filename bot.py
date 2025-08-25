import os
import random
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Данные бота
TOKEN = os.environ.get('TOKEN')  # Токен берется из переменных окружения

# Списки данных
RAILWAY_STATIONS = {
    "Белорусский": ["Одинцово", "Кубинка", "Звенигород", "Трехгорка", "Голицыно", "Тучково", "Можайск", "Сетунь"],
    "Казанский": ["Голутвин", "Люберцы", "Раменское", "Шатура"],
    "Киевский": ["Переделкино", "Очаково", "Нара", "Балабаново", "Обнинск", "Лесной городок", "Малоярославец"],
    "Курский": ["Подольск", "Щербинка", "Чехов", "Серпухов", "Тула"],
    "Ленинградский": ["Крюково", "Химки", "Клин", "Сходня", "Подсолнечная", "Ховрино"],
    "Павелецкий": ["Ступино", "Бирюлево", "Расторгуево", "Кашира", "Узуново", "Барыбино"],
    "Рижский": ["Волоколамск", "Нахабино", "Истра", "Новоиерусалимская", "Румянцево"],
    "Савеловский": ["Лобня", "Дмитров", "Долгопрудная", "Дубна", "Большая Волга", "Бескудниково", "Водники", "Катуар"],
    "Ярославский": ["Сергиев Посад", "Пушкино", "Монино", "Александров", "Фрязино", "Болшево", "Мытищи"]
}

# Клавиатуры
main_keyboard = ReplyKeyboardMarkup([['🚂 Сгенерировать маршрут']], resize_keyboard=True)
back_keyboard = ReplyKeyboardMarkup([['🔙 Назад']], resize_keyboard=True)

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚉 Добро пожаловать в бот для генерации маршрутов!\n\n"
        "Нажмите '🚂 Сгенерировать маршрут' для получения случайного маршрута.",
        reply_markup=main_keyboard
    )

async def generate_route(update: Update, context: ContextTypes.DEFAULT_TYPE):
    station = random.choice(list(RAILWAY_STATIONS.keys()))
    direction = random.choice(RAILWAY_STATIONS[station])
    station_number = random.randint(10, 30)
    
    response = (
        f"🚂 <b>Ваш вокзал:</b> {station}\n"
        f"📍 <b>Направление:</b> Москва — {direction}\n"
        f"🔢 <b>Станция для выхода:</b> {station_number}\n\n"
        f"Приятного путешествия! 🌟"
    )
    
    await update.message.reply_text(response, parse_mode='HTML', reply_markup=back_keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == '🚂 Сгенерировать маршрут':
        await generate_route(update, context)
    elif text == '🔙 Назад':
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=main_keyboard
        )
    else:
        await update.message.reply_text(
            "Используйте кнопки для навигации",
            reply_markup=main_keyboard
        )

# Основная функция
def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()