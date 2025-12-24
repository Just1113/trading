from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Trading bot is online.")

async def send_startup_message(app):
    await app.bot.send_message(
        chat_id=ADMIN_ID,
        text="Trading bot has started successfully on Render."
    )

def start_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.post_init = send_startup_message

    print("Telegram bot started")
    app.run_polling()
