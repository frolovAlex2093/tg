import asyncio
from aiogram import Bot, Dispatcher
from handlers import register_common_handlers, register_income_handlers

async def main():
    bot = Bot(token="7515723134:AAFMX449trE4aD2ODHPwfdmlsCfvv-gKlUM")
    dp = Dispatcher()

    # Регистрация обработчиков
    register_common_handlers(dp)
    register_income_handlers(dp)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())