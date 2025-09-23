from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

# Bot token-kaaga halkan ku dhig
BOT_TOKEN = "8293803625:AAEQH1ku0CXDoWCBkr8V82g5_7ZJmAArTxk"

# Command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot-ka waa online oo wuu shaqeynayaa!")

def main():
    # Abuur app
    app = Application.builder().token(BOT_TOKEN).build()

    # Ku dar handler /start
    app.add_handler(CommandHandler("start", start))

    # Polling start
    print("🤖 Bot-ka wuu socdaa...")
    app.run_polling()

if __name__ == "__main__":
    main()
