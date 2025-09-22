import os
import asyncio
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN", "8293803625:AAGiG8avn7Y0TpJSqu5NZWDqoCUGwiPw-WU")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@betting_Bot_somalia")  # ama private ID: -100xxxxxxx

async def main():
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHANNEL_ID, text="Bot-kan waa online!")

if __name__ == "__main__":
    asyncio.run(main())
