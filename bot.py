import os
import asyncio
import random
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import datetime

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Render environment variable
CHANNEL_USERNAME = os.getenv("CHANNEL_ID")  # Render environment variable, e.g. "@betting_Bot_somalia"
PROMO_CODE = "ABAANA777"

TEAMS = ["Team A", "Team B", "Team C", "Team D", "Team E"]
ICONS = ["⚽", "🔥", "💰", "🏆", "🎯"]

# ===== Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello! 🤖\nBot-ka diyaar ayuu u yahay sports tips & promo code-kaaga.\n"
        f"Promo code maanta: {PROMO_CODE}"
    )

async def betting_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips = []
    for i in range(10):
        team = random.choice(TEAMS)
        odds = round(random.uniform(1.5, 3.5), 2)
        probability = random.choice(["95%", "💯%"])
        icon = random.choice(ICONS)
        tips.append(f"{icon} Tip {i+1}: {team} @ odds {odds} ({probability})")
    message = "\n".join(tips)
    message += f"\n\n💡 Promo code: {PROMO_CODE}"
    if update:
        await update.message.reply_text(message)
    else:
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=CHANNEL_USERNAME, text=message)

async def reply_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "new sports" in text or "tips" in text:
        await betting_tips(update, context)
    elif "sub affiliate" in text:
        await update.message.reply_text(
            f"Si aad sub-affiliate u noqoto, isticmaal promo code: {PROMO_CODE} 🤝"
        )
    elif "promo code" in text:
        await update.message.reply_text(f"Promo code-ka maanta: {PROMO_CODE} 💎")
    else:
        await update.message.reply_text(
            "Ma fahmin su'aashaas. Waxaad weydiin kartaa 'new sports', 'tips', ama 'sub affiliate'."
        )

# ===== Scheduler for daily tips =====
async def daily_tips_scheduler():
    while True:
        now = datetime.datetime.now()
        # Tusaale: Send at 12:00 PM
        if now.hour == 12 and now.minute == 0:
            await betting_tips(None, None)  # None update = send to channel
            await asyncio.sleep(60)  # Prevent double send in same minute
        await asyncio.sleep(30)

# ===== Main =====
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("tips", betting_tips))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_questions))

    # Start bot
    await app.start()
    await app.updater.start_polling()
    print("Bot-ka waa online!")

    # Start daily tips scheduler
    asyncio.create_task(daily_tips_scheduler())

    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
