from aiogram import Router, F
from aiogram.filters import  Command
from aiogram.types import Message, CallbackQuery
from app.keyboards import currency_keyboard, keyboard_of_abil, stop_operation
from app.database import validation, save_currency, daily_count

import aiohttp
import asyncio

router1 = Router()

translate = {
    'USD': '🇺🇸 Доллар США',
    'EUR': '🇪🇺 Евро',
    'CZK': '🇨🇿 Чешская крона',
    'PLN': '🇵🇱 Польский злотый',
    'MDL': '🇲🇩 Молдавский лей',
    'AZN': '🇦🇿 Азербайджанский манат',
    'RON': '🇷🇴 Румынский лей',
    'UAH': '🇺🇦 Украинская гривна'
}


@router1.message(Command('currency'))
async def currency(message: Message):
    count = await validation(message.from_user.id, 'currency_count')
    if count is None:
        count = 0
    if count >= 10:
        await message.answer("Упс 😅, вы уже использовали все свои запросы на сегодня. \n"
                            "Приходите завтра, чтобы проверить курсы валют снова!")
        return
    user_curr = await validation(message.from_user.id, 'currency')
    if user_curr is None:
        await message.answer(f'Вы ещё не указали валюту, для которой хотите узнать курc😅', reply_markup=stop_operation)
        await message.answer('💱Выберете одну из валют ниже:', reply_markup=currency_keyboard)
    else:
        result = await currency_get_inf(user_curr)
        for item in range(len(result)):
            result[item][0]['txt'] = translate[result[item][0]['cc']]
        answer_to_bot = await currency_answer_creating(result, user_curr)
        await message.answer("\n".join(answer_to_bot))
        await daily_count(message.from_user.id, 'currency_count')
        attempts = 9-count
        if attempts == 0:
            await message.answer(f"💱 Осталось {attempts} запросов на курсы валют сегодня.\n"
                                "Приходите завтра 😊")
        else:
            await message.answer(f"💱 Осталось {attempts} запросов на курсы валют сегодня.")

@router1.message(Command('change_currency'))
async def change_currency(message: Message):
    current_currency = await validation(message.from_user.id, 'currency')
    if current_currency is None:
        await currency(message)
    else:
        await message.answer(f"🌟 Ваша валюта на данный момент: {translate[str(current_currency)]}/{current_currency}\n", reply_markup=stop_operation)
        await message.answer(f'💱 Выберите валюту ниже: ', reply_markup=currency_keyboard)

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

async def fetch_currency(session, valcode):
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    params = {"valcode":valcode}
    async with session.get(url, params=params) as response:
        return await response.json()


async def currency_get_inf(user_curr):
    list_of_currency = ['USD', 'EUR', 'CZK', 'PLN', 'MDL', 'AZN', 'RON']
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_currency(session, item) for item in list_of_currency]
        results = await asyncio.gather(*tasks)
        results.append([{'r030': 0, 'txt': '', 'rate': 1, 'cc': 'UAH'}])
        return results
    
async def currency_answer_creating(currencies, user_curr):
    found = next((lst for lst in currencies if lst[0].get('cc') == user_curr), None)
    text = [f'Ваша валюта💵: {found[0]['txt']}/{found[0]['cc']}',
            f'💱 Курсы валют на сегодня:']
    
    for item in currencies:
        if item[0]['cc'] != str(user_curr):
            calc = round(item[0]['rate']/found[0]['rate'], 4)
            text.append(
                f'1 {item[0]['cc']} = {calc} {user_curr} 💰'
            )
    return text