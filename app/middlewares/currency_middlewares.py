from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Awaitable, Dict, Any

from app.services.currency_serv import CurrencyHandler

class SingleObjectCurrencyMiddleware(BaseMiddleware):
    def __init__(self, instance: CurrencyHandler):
        self.instance = instance
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:
        data['singleobjcurrencymiddleware'] = self.instance
        return await handler(event, data)