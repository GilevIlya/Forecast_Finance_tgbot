from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from redis_client import REDIS
from typing import Callable, Awaitable, Dict, Any

class MessageLimitMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:
        if isinstance(event, Message):
            current_numb_of_messages = REDIS.get(f'{data['event_context'].chat.id}')
            if current_numb_of_messages is None:
                print('No redis')
                REDIS.set(f'{data['event_context'].chat.id}', 1, ex=10)
                return await handler(event, data)
            if int(current_numb_of_messages.decode()) >= 5:
                event.answer('Limit got')
                return
            print('Went through')
            REDIS.incr(f'{data['event_context'].chat.id}')
        return await handler(event, data)