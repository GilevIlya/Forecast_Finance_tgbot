from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import reset_weather_currency_at_midnight_db, update_db_currency_data
from redis_client import rds_client
from aiogram import Bot
from pytz import timezone

import aiohttp
import asyncio
import os
import json

ADMIN_ID = os.getenv('ADMIN_ID')
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)

async def reset_weather_currency_at_midnight():
    scheduler = AsyncIOScheduler(timezone=timezone("Europe/Kyiv"))
    scheduler.add_job(reset_weather_currency_at_midnight_db, 'cron', hour=0, minute=0)
    scheduler.start()

async def update_currency():
    scheduler2 = AsyncIOScheduler(timezone=timezone("Europe/Kyiv"))
    scheduler2.add_job(run_update,'interval', seconds=10800)
    scheduler2.start()

# ========================
# UPDATE CURRENCY FOR DB🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# ========================


class CurrencyUpdate:
    def __init__(self):
        self.translate_currencies = {
            'USD': '🇺🇸 Доллар США',
            'EUR': '🇪🇺 Евро',
            'CZK': '🇨🇿 Чешская крона',
            'PLN': '🇵🇱 Польский злотый',
            'MDL': '🇲🇩 Молдавский лей',
            'AZN': '🇦🇿 Азербайджанский манат',
            'RON': '🇷🇴 Румынский лей',
            'UAH': '🇺🇦 Украинская гривна'
        }
    async def currency_http_request(self, session, valcode):
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        params = {"valcode": valcode}
        async with session.get(url, params=params) as response:
            return await response.json()

    async def create_db_insert_data(self, currency_inf):
        dict_of_currency = {
                'USD': {},
                'EUR': {},
                'CZK': {},
                'PLN': {},
                'MDL': {},
                'AZN': {},
                'RON': {},
                'UAH': {}
            }
        for item in currency_inf:
            for other_item in currency_inf:
                if other_item == item:
                    continue
                else:
                    dict_of_currency[item[0]['cc']][other_item[0]['cc']] = round(other_item[0]['rate']/item[0]['rate'], 6)
        return dict_of_currency


    async def currency_get_inf(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.currency_http_request(session, item) for item in self.translate_currencies.keys() if item != 'UAH']
            results = await asyncio.gather(*tasks)
            results.append([{'r030': 0, 'txt': '', 'rate': 1, 'cc': 'UAH'}])
            final_data = await self.create_db_insert_data(results)
            return final_data

async def run_update():
    cur = CurrencyUpdate()
    final_data = await cur.currency_get_inf()
    json_final_data = json.dumps(final_data)
    rds_client.set('currency_data', json_final_data, ex=10800)
    await update_db_currency_data(json_final_data)


# ========================
# UPDATE CURRENCY FOR DB 🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
# ========================