from config import TOKEN
from aiogram import Bot, Dispatcher
from aiogram import Router
from app.database import close_pool, create_pool
from app.handlers.sheduler import weather_forallusers_to0
from app.handlers.weather import router
from app.handlers.currency import router1
import asyncio

routermain = Router()
routermain.include_routers(router, router1)

bot = Bot(token=TOKEN)
dp = Dispatcher()
async def run_bot():
    await create_pool()
    try:
        dp.include_router(routermain)
        await weather_forallusers_to0()
        await dp.start_polling(bot)
    finally:
        await close_pool()

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print('Stop')