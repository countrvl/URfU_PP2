import asyncio
import logging
import sys
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from common.startup import on_startup
from handlers.registration import registration_router
from handlers.reserves import reserves_router
from handlers.spots import spots_router
from handlers.start import start_router
from handlers.cars import cars_router

TOKEN = os.getenv("TELEGRAM_BOT_BOOKING_API_KEY")

dp = Dispatcher()
dp.include_routers(
    start_router,
    registration_router,
    spots_router,
    reserves_router,
    cars_router,
)
dp.startup.register(on_startup)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())