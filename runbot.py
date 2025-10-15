from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Update
from aiohttp import web
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
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def webhook_handler(request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(text="OK")

async def health_check(request):
    await bot.send_message(ADMIN_ID, 'awake, uptimerobot')
    return web.Response(text="Bot is running!")

async def on_startup(app):
    await create_pool()
    await reset_weather_currency_at_midnight()
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    if not WEBHOOK_URL:
        print("WEBHOOK_URL не установлен! Добавьте переменную окружения.")
        return
    try:
        await bot.set_webhook(
            url=f"{WEBHOOK_URL}/webhook",
            drop_pending_updates=True
        )
        print(f"✅ Webhook установлен: {WEBHOOK_URL}/webhook")
    except Exception as e:
        print(f"Не удалось установить webhook: {e}")
        print(f"Проверьте что домен доступен: {WEBHOOK_URL}")

async def on_shutdown(app):
    await close_pool()
    await bot.delete_webhook()

async def main():
    dp.include_router(routermain)
    app = web.Application()
    app.router.add_post('/webhook', webhook_handler)
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    PORT = int(os.getenv('PORT', 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('🛑 Остановка...')