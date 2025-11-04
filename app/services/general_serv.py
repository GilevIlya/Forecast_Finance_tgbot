from aiogram.types import Message
from app.database import daily_count


class CurrencyAndWeatherHandlerMainClass:
    def __init__(self):
        pass

    async def _is_limit_reached(self, limit: int, user_attempts: int) -> bool:
        return limit <= user_attempts if user_attempts else 0

    async def _count_message(self, limit: int, user_attempts: int, message: Message, **kwargs) -> None:
        attempts_left = (limit - 1) - user_attempts
        is_limit_reached = attempts_left <= 0

        weather_config = kwargs.get('weather_config')
        if weather_config:
            desc = weather_config['desc']
            base_text = f"☁️ Осталось всего {attempts_left} запрос(ов) узнать {desc} сегодня!"
        else:
            base_text = f"💱 Осталось {attempts_left} запрос(ов) на курсы валют сегодня."

        if is_limit_reached:
            base_text += "\nПриходите завтра 😊"
        await message.answer(base_text)

    async def _update_counter(self, user_id: int, key: str) -> None:
        await daily_count(user_id, key)