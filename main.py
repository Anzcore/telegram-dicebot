import os
import logging
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен из переменной окружения
TOKEN = os.environ["TELEGRAM_TOKEN"]

# Flask-приложение
app = Flask(__name__)

# Telegram Application
bot_app = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Используй команду /roll, чтобы бросить d20 🎲")

# Команда /roll
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random
    result = random.randint(1, 20)
    if result == 20:
        text = "🎲 Ты бросил 20! Критический успех! 🎉"
    elif result == 1:
        text = "🎲 Ты бросил 1... Критическая неудача! 💀"
    else:
        text = f"🎲 Ты бросил {result}"
    await update.message.reply_text(text)

# Регистрируем обработчики
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("roll", roll))

# Главная страница для проверки
@app.route('/')
def index():
    return {"message": "DiceBot is running!"}

# Обработка Telegram webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        from telegram import Update
        import asyncio

        data = request.get_json(force=True)
        update = Update.de_json(data, bot_app.bot)

        async def handle():
            await bot_app.initialize()
            await bot_app.process_update(update)

        asyncio.run(handle())  # ← это единственная async строка
        return 'ok'
    else:
        abort(403)

# Локальный запуск (если нужен)
if __name__ == "__main__":
    app.run(port=5000)