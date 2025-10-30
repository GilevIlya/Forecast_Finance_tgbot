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
    count = await validation(message.from_user.id, 'currency_count')
    count = 0 if count is None else count
    if count >= 10:
        await message.answer("Упс 😅, вы уже использовали все свои запросы на сегодня. \n"
                            "Приходите завтра, чтобы проверить курсы валют снова!")
        return
    user_curr = await validation(message.from_user.id, 'currency')
    if user_curr is None:
        await message.answer(f'Вы ещё не указали валюту, для которой хотите узнать курc😅', reply_markup=stop_operation)
        await message.answer('💱Выберете одну из валют ниже:', reply_markup=currency_keyboard)
    else:
        message_ans = await create_currency_answer(user_curr, count)
        await message.answer(message_ans)
        attempts = 9 - count
        if attempts == 0:
            await message.answer(f"💱 Осталось {attempts} запросов на курсы валют сегодня.\n"
                                    "Приходите завтра 😊")
        else:
            await message.answer(f"💱 Осталось {attempts} запросов на курсы валют сегодня.")
        await daily_count(message.from_user.id, 'currency_count')

async def create_currency_answer(user_curr, count):
    currency_for_user = await get_curr_from_db(user_curr)
    count = await validation(count, 'currency_count')
    base_currency = list(currency_for_user.keys())[0]
    message_lines = [
        f"💱 Курсы валют относительно {base_currency}/{translate[base_currency]}:",
        "------------------------------------"
    ]
    for currency, value in currency_for_user[base_currency].items():
        message_lines.append(f"• {currency}/{translate[currency]}: {value:.4f}")
    message_lines.append("------------------------------------")
    today = date.today()
    message_lines.append(f"🛈 Данные актуальны на {today}.")
    return "\n".join(message_lines)


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