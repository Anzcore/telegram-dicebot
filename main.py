import os
import random
import logging
import asyncio
from flask import Flask, request, abort
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    MessageHandler, filters
)

# Логирование
logging.basicConfig(level=logging.INFO)

# Токен из переменной окружения
TOKEN = os.environ["TELEGRAM_TOKEN"]

# Flask-приложение
app = Flask(__name__)

# Telegram-приложение
bot_app = Application.builder().token(TOKEN).build()

# --- Команды и сообщения ---

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("🎲 Бросить d20")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Нажми кнопку ниже, чтобы бросить кубик:",
        reply_markup=reply_markup
    )

# Бросок по кнопке
async def handle_roll_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🎲 Бросить d20":
        result = random.randint(1, 20)
        if result == 20:
            msg = "🎲 Ты бросил 20! Критический успех! 🎉"
        elif result == 1:
            msg = "🎲 Ты бросил 1... Критическая неудача! 💀"
        else:
            msg = f"🎲 Ты бросил {result}"
        await update.message.reply_text(msg)

# --- Обработчики ---

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_roll_button))

# --- Flask Webhook ---

@app.route("/")
def index():
    return {"message": "DiceBot is running!"}

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        data = request.get_json(force=True)
        update = Update.de_json(data, bot_app.bot)

        async def process():
            await bot_app.initialize()
            await bot_app.process_update(update)

        asyncio.run(process())
        return "ok"
    else:
        abort(403)

# --- Локальный запуск (если нужно) ---
if __name__ == "__main__":
    app.run(port=5000)
