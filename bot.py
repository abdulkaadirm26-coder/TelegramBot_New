from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8293803625:AAEQH1ku0CXDoWCBkr8V82g5_7ZJmAArTxk"
CHANNEL_ID = "@betting_Bot_somalia"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salaan 👋 Bot-kan waa online! ✅\nPromo code: ABAANA777"
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHANNEL_ID, text="Bot-kan waa online! ✅")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))
    print("Bot is running... ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
  
