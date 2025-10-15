from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import reset_weather_currency_at_midnight_db
from app.handlers.weather import TOKEN, ADMIN_ID
from aiogram import Bot

bot = Bot(token=TOKEN)

async def reset_weather_currency_at_midnight():
    sheduler = AsyncIOScheduler()
    sheduler.add_job(reset_weather_currency_at_midnight_db, 'cron', hour=0, minute=0)
    sheduler.start()