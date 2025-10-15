from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram import Router
from app.database import close_pool, create_pool
from app.handlers.sheduler import reset_weather_currency_at_midnight
from app.handlers.weather import router
from app.handlers.currency import router1

import asyncio
import os

routermain = Router()
routermain.include_routers(router, router1)

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()
async def run_bot():
    await create_pool()
    try:
        dp.include_router(routermain)
        await reset_weather_currency_at_midnight()
        await dp.start_polling(bot)
    finally:
        await close_pool()

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print('Stop')