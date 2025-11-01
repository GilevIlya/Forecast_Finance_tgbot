from aiogram import Router, F
from aiogram.filters import  Command
from aiogram.types import Message, CallbackQuery
from app.keyboards import currency_keyboard, keyboard_of_abil, stop_operation
from app.database import validation, save_currency, daily_count, get_curr_from_db
from datetime import date

import aiohttp
import asyncio

router1 = Router()

translate = {
    'USD': '🇺🇸 Доллар США',
    'EUR': '🇪🇺 Евро',
    'CZK': '🇨🇿 Чешская крона',
    'PLN': '🇵🇱 Польский злотый',
    'MDL': '🇲🇩 Молдавский лей',
    'AZN': '🇦🇿 Азербайдж. манат',
    'RON': '🇷🇴 Румынский лей',
    'UAH': '🇺🇦 Украинская гривна'
}


# COMMANDS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# COMMANDS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# COMMANDS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽


@router1.message(F.text.in_(['/currency', '💱 Курс валют']))
async def currency(message: Message):
    currency_user = CurrencyHandler(message)
    await currency_user.main_process()

@router1.message(Command('change_currency'))
async def change_currency(message: Message):
    current_currency = await validation(message.from_user.id, 'currency')
    if current_currency is None:
        await currency(message)
    else:
        await message.answer(f"🌟 Ваша валюта на данный момент: {translate[str(current_currency)]}/{current_currency}\n", reply_markup=stop_operation)
        await message.answer(f'💱 Выберите валюту ниже: ', reply_markup=currency_keyboard)

#COMMANDS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
#COMMANDS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
#COMMANDS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼




# CALLBACKS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# CALLBACKS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# CALLBACKS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽

@router1.callback_query(F.data.startswith('cur'))
async def reg_currency(callback: CallbackQuery):
    try:
        _, currency_name = callback.data.split(':')
        await save_currency(callback.from_user.id, currency_name)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text=f'🔥Теперь ваша валюта {translate[currency_name]}/{currency_name} сохранена.Что будем делать дальше?', 
                                      reply_markup=keyboard_of_abil)
    except:
        await callback.answer('Error')

#CALLBACKS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
#CALLBACKS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
#CALLBACKS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼


class CurrencyHandler:
    def __init__(self, message):
        self.message = message
        self.user_id = message.from_user.id
        self.curr_calls_limit = 10

    async def main_process(self):
        if await self.__is_limit_reached():
            await self.message.answer("Упс 😅, вы уже использовали все свои запросы на сегодня. \n"
                                      "Приходите завтра, чтобы проверить курсы валют снова!")
            return
        self.user_curr = await validation(self.user_id, 'currency')
        if self.user_curr is None:
            return await self.ask_for_currency()
        await self.message.answer('⏳ Подождите...')
        await self.create_currency_answer(self.user_curr)
        await self.counter_message()
        await self.update_counter()

    async def __is_limit_reached(self):
        self.user_attempts = await validation(self.user_id, 'currency_count')
        return self.curr_calls_limit <= self.user_attempts if self.user_attempts else 0

    async def ask_for_currency(self):
        await self.message.answer(f'Вы ещё не указали валюту, для которой хотите узнать курc😅',
                                  reply_markup=stop_operation)
        await self.message.answer('💱Выберете одну из валют ниже:', reply_markup=currency_keyboard)

    async def create_currency_answer(self, user_curr):
        curr_data_for_user = await get_curr_from_db(user_curr)
        base_currency_name = list(curr_data_for_user.keys())[0]
        message_lines = [
            f"💱 Курсы валют относительно {base_currency_name}/{translate[base_currency_name]}:",
            "------------------------------------"
        ]
        for currency, value in curr_data_for_user[base_currency_name].items():
            message_lines.append(f"• {currency}/{translate[currency]}: {value:.4f}")
        message_lines.append("------------------------------------")
        today = date.today()
        message_lines.append(f"🛈 Данные актуальны на {today}.")
        await self.message.answer("\n".join(message_lines))

    async def count_message(self):
        attempts_left = ((self.curr_calls_limit - 1) - self.user_attempts)
        await self.message.answer(f"💱 Осталось {attempts_left} запросов на курсы валют сегодня.\n"
                                  "Приходите завтра 😊" if attempts_left == 0 else
                                  (f"💱 Осталось {attempts_left} запросов на курсы валют сегодня."))

    async def update_counter(self):
        await daily_count(self.user_id, 'currency_count')