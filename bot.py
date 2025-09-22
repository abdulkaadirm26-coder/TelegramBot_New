from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ===========
# SETTINGS - HALKAN ADIGA BUUXI
# ===========
BOT_TOKEN = "8293803625:AAEQH1ku0CXDoWCBkr8V82g5_7ZJmAArTxk"   # Bot token-kaaga
CHANNEL_ID = "@betting_Bot_somalia"  # Channel username-kaaga

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salaan 👋 Bot-kan waa online! ✅\n"
        "Waxaad ka hubin kartaa channel-ka inuu si sax ah u shaqeynayo.\n"
        "Promo code: ABAANA777"
    )

# Test command
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="Bot-kan waa online! ✅"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))

    print("Bot is running... ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
