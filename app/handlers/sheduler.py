from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import weather_forallusers_to0_db

async def weather_forallusers_to0():
    sheduler = AsyncIOScheduler()
    sheduler.add_job(weather_forallusers_to0_db, 'cron', hour=0, minute=0)
    sheduler.start()