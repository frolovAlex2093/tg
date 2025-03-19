import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import register_common_handlers, register_income_handlers

load_dotenv()

async def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("Не задан токен бота! Укажите его в .env")

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    register_common_handlers(dp)
    register_income_handlers(dp)

    await dp.start_polling(bot)

if __name__ == "main":
    asyncio.run(main())