from aiogram.types import (ReplyKeyboardMarkup,InlineKeyboardButton
                           ,InlineKeyboardMarkup,KeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder 

stop_operation = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🛑Прервать операцию')]
], resize_keyboard=True, one_time_keyboard=True)

async def build_city_keyboard(cities):
    builder = InlineKeyboardBuilder()
    for i in cities:
        btn_text = f'{i[0]}, {i[1]}, {i[2]}'
        callback_data_city = f"set_city:{i[3]}:{i[4]}:{i[0]}"
        builder.add(InlineKeyboardButton(text=btn_text, callback_data=callback_data_city))
        builder.adjust(1)
        keyboard = builder.as_markup()
    return keyboard

replacing_keyboard = InlineKeyboardMarkup(inline_keyboard=[])

keyboard_of_abil = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🌦 Погода"), KeyboardButton(text="☀️Погода на 5 дней")],
        [KeyboardButton(text="🏠 Главное меню"), KeyboardButton(text="💱 Курс валют")]
    ],resize_keyboard=True)

currency_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='UAH', callback_data='cur:UAH'), InlineKeyboardButton(text='USD', callback_data='cur:USD')],
    [InlineKeyboardButton(text='EUR', callback_data='cur:EUR'), InlineKeyboardButton(text='AZN', callback_data='cur:AZN')],
    [InlineKeyboardButton(text='CZK', callback_data='cur:CZK'), InlineKeyboardButton(text='PLN', callback_data='cur:PLN')],
    [InlineKeyboardButton(text='MDL', callback_data='cur:MDL'), InlineKeyboardButton(text='RON', callback_data='cur:RON')]
])