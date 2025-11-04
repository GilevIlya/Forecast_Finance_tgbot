from aiogram.types import Message, CallbackQuery
from app.keyboards import stop_operation, keyboard_of_abil, currency_keyboard
from app.services.general_serv import CurrencyAndWeatherHandlerMainClass
from app.database import validation, get_curr_from_db, save_currency
from datetime import date

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

class CurrencyHandler(CurrencyAndWeatherHandlerMainClass):
    async def main_process(self, message: Message):
        user_id = message.from_user.id
        user_attempts = await validation(user_id, 'currency_count')
        limit = 10
        if await self._is_limit_reached(limit, user_attempts):
            await message.answer("Упс 😅, вы уже использовали все свои запросы на сегодня. \n"
                                      "Приходите завтра, чтобы проверить курсы валют снова!")
            return
        user_curr = await validation(user_id, 'currency')
        if user_curr is None:
            return await self.ask_for_currency(message)
        await message.answer('⏳ Подождите...')
        await self.create_currency_answer(user_curr, message)
        await self._count_message(limit, user_attempts, message)
        await self._update_counter(user_id, 'currency_count')

    async def ask_for_currency(self, message: Message) -> None:
        await message.answer(f'Вы ещё не указали валюту, для которой хотите узнать курc😅',
                                  reply_markup=stop_operation)
        await message.answer('💱Выберете одну из валют ниже:', reply_markup=currency_keyboard)

    async def create_currency_answer(self, user_curr: str, message: Message) -> None:
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
        message_lines.append(f"Upd 🛈 Данные актуальны на {today}.")
        await message.answer("\n".join(message_lines))

async def changing_currency(message: Message, singleobjcurrencymiddleware: CurrencyHandler):
    current_currency = await validation(message.from_user.id, 'currency')
    if current_currency is None:
        await singleobjcurrencymiddleware.main_process(message)
    else:
        await message.answer(f"🌟 Ваша валюта на данный момент: {translate[str(current_currency)]}/{current_currency}\n",
                             reply_markup=stop_operation)
        await message.answer(f'💱 Выберите валюту ниже: ', reply_markup=currency_keyboard)

async def process_saving_currency(callback: CallbackQuery):
    try:
        _, currency_name = callback.data.split(':')
        await save_currency(callback.from_user.id, currency_name)
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text=f'🔥Теперь ваша валюта {translate[currency_name]}/{currency_name} сохранена.Что будем делать дальше?',
                                      reply_markup=keyboard_of_abil)
    except:
        await callback.answer('Error')