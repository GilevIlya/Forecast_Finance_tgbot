from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from redis_client import rds_client
from typing import Callable, Awaitable, Dict, Any

class MessageLimitMiddleware(BaseMiddleware): 
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any],
                       ) -> Any:
        if not isinstance(event, Message): 
            return await handler(event, data) 
        chat_id = data['event_context'].chat.id 
        key = f"{chat_id}" 
        current = rds_client.get(key) 
        if current is None: 
            rds_client.set(key, 1, ex=10) 
            return await handler(event, data) 
        current = int(current.decode()) 
        if current >= 5: 
            await event.answer("Похоже, ты слишком активен! ⏳ Сделай паузу и попробуй через несколько секунд.") 
            return None
        rds_client.incr(key)
        return await handler(event, data)