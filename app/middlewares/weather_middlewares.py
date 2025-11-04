from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Awaitable, Dict, Any

from app.services.weather_serv import WeatherCommandsHandler

class SingleObjectWeatherMiddleware(BaseMiddleware):
    def __init__(self, instance: WeatherCommandsHandler):
        self.instance = instance
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:
        data['singleobjweathermiddleware'] = self.instance
        return await handler(event, data)