from aiogram import Router, F, Bot
from aiogram.filters import  Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, TelegramObject
from aiogram.fsm.context import FSMContext
from app.middlewares.weather_middlewares import SingleObjectWeatherMiddleware
from app.services.weather_serv import (
    Register,
    process_start_command,
    register_city_FSMContext,
    WeatherCommandsHandler,
    process_change_city,
    save_new_location,
    process_help_command,
)

import os

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
router = Router()

instance = WeatherCommandsHandler()
router.message.middleware(SingleObjectWeatherMiddleware(instance))

@router.message(Command('help'))
async def help_command(message: Message):
    await process_help_command(message)

@router.message(Command('start'))
async def start_command(message: Message):
    await process_start_command(message)

@router.message(F.text.in_(['/weather_week', '/weather', '🌦 Погода', '☀️Погода на 5 дней']))
async def weather_command(message: Message, state: FSMContext, singleobjweathermiddleware: WeatherCommandsHandler):
    await singleobjweathermiddleware.main_process(message, state)

@router.message(Command('change_city'))
async def change_city(message:Message, state:FSMContext):
    await process_change_city(message, state)

@router.message(F.text.in_(['🏠 Главное меню', '🛑Прервать операцию']))
async def menu_or_cancel_handler(message:Message, state:FSMContext):
    if message.text == "🏠 Главное меню":
        await start_command(message)
    elif message.text == '🛑Прервать операцию':
        await state.clear()
        await message.answer("❌ Операция прервана", reply_markup=ReplyKeyboardRemove())
        await start_command(message)

@router.message(Register.city)
async def save_location(message: Message, state:FSMContext):
    await register_city_FSMContext(message, state)

@router.callback_query(F.data.startswith('set_city'))
async def get_new_location(callback:CallbackQuery, state:FSMContext):
    await save_new_location(callback, state)