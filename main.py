import os
import logging
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Telegram Bot Token
TOKEN = os.environ["TELEGRAM_TOKEN"]

# Flask app
app = Flask(__name__)

# Telegram app
bot_app = Application.builder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Используй /roll, чтобы бросить d20 🎲")

# Команда /roll
async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import random
    value = random.randint(1, 20)
    if value == 20:
        msg = "🎲 Ты бросил 20! Критический успех! 🎉"
    elif value == 1:
        msg = "🎲 Ты бросил 1... Критическая неудача! 💀"
    else:
        msg = f"🎲 Ты бросил {value}"
    await update.message.reply_text(msg)

# Регистрируем команды
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("roll", roll))

@app.route('/')
def index():
    return {"message": "DiceBot is running!"}

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        data = request.get_json(force=True)
        update = Update.de_json(data, bot_app.bot)

        import asyncio

        async def process():
            await bot_app.initialize()                # 🟢 обязательно!
            await bot_app.process_update(update)     # 🟢 и только потом обработка

        asyncio.run(process())  # 👈 это правильно вместо get_event_loop()
        return 'ok'
    else:
        abort(403)

if __name__ == "__main__":
    app.run(port=5000)
