from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import reset_weather_currency_at_midnight_db
from app.handlers.weather import TOKEN, ADMIN_ID
from aiogram import Bot
from pytz import timezone

bot = Bot(token=TOKEN)

async def reset_weather_currency_at_midnight():
    scheduler = AsyncIOScheduler(timezone=timezone("Europe/Kyiv"))
    scheduler.add_job(reset_weather_currency_at_midnight_db, 'cron', hour=0, minute=0)
    scheduler.start()