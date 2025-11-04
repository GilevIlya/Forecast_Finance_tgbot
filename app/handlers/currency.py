from aiogram import Router, F
from aiogram.filters import  Command
from aiogram.types import Message, CallbackQuery
from app.services.currency_serv import CurrencyHandler, changing_currency, process_saving_currency
from app.middlewares.currency_middlewares import SingleObjectCurrencyMiddleware

instance = CurrencyHandler()

router1 = Router()
router1.message.middleware(SingleObjectCurrencyMiddleware(instance))

@router1.message(F.text.in_(['/currency', '💱 Курс валют']))
async def currency_command(message: Message, singleobjcurrencymiddleware: CurrencyHandler):
    await singleobjcurrencymiddleware.main_process(message)

@router1.message(Command('change_currency'))
async def change_currency(message: Message, singleobjcurrencymiddleware: CurrencyHandler):
    await changing_currency(message, singleobjcurrencymiddleware)

@router1.callback_query(F.data.startswith('cur'))
async def save_currency(callback: CallbackQuery):
    await process_saving_currency(callback)