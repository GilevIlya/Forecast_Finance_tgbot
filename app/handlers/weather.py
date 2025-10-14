from aiogram import Router, F, Bot
from aiogram.filters import  Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from app.keyboards import build_city_keyboard, keyboard_of_abil, stop_operation
from app.database import save_city_and_coords, validation, registration, daily_count 
from app.handlers.currency import currency
from config import API_KEY, ADMIN_ID, ADMIN_USER_NAME, TOKEN
from datetime import datetime

import aiohttp
import json

bot = Bot(token=TOKEN)
router = Router()

###################################################################
# INDEPENDENT COMMAND "/help"
@router.message(Command('help'))
async def help(message: Message):
    await message.answer(
        "🤖 <b>Привет!</b> Я бот <b>Forecast&Finance</b> 🌦💸\n"
        "Помогаю узнавать <b>погоду</b> и <b>курсы валют</b>.\n\n"

        "📋 <b>Доступные команды:</b>\n"
        "• /start — начать работу\n"
        "• /weather — прогноз погоды\n"
        "• /change_city — изменить город 🌍\n"
        "• /currency — курсы валют 💱\n"
        "• /change_currency — выбрать валюту 💰\n"
        "• /help — помощь\n\n"

        "📊 <b>Пример прогноза:</b>\n"
        "🌍 Город: Лос-Анджелес, US\n"
        "🌡 Темп: 21.5°C (ощущается как 21.2°C)\n"
        "📉 Мин: 20.0°C / Макс: 22.7°C\n"
        "☁️ Погода: небольшая облачность\n"
        "💨 Ветер: 6.7 м/с\n"
        "💧 Влажность: 57%\n"
        "🌅 Восход: 16:56 | 🌇 Закат: 04:21\n\n"

        "💱 <b>Пример курсов валют:</b>\n"
        "Ваша валюта: 🇺🇦 Гривна (UAH)\n"
        "1 USD = 41.61 UAH\n"
        "1 EUR = 48.13 UAH\n"
        "1 PLN = 11.29 UAH\n"
        "1 CZK = 1.98 UAH\n"
        "1 MDL = 2.46 UAH\n"
        "1 AZN = 24.48 UAH\n"
        "1 RON = 9.46 UAH\n\n"

        f"📨 По вопросам — @{ADMIN_USER_NAME}"
        , parse_mode="HTML"
    )

# INDEPENDENT COMMAND "/help"
###################################################################




# COMMANDS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# COMMANDS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# COMMANDS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽

@router.message(Command('start'))
async def reg_user(message: Message):
    if await validation(message.from_user.id, 'id') is None:
        await registration(message.from_user.id, 
                           message.from_user.first_name, 
                           message.from_user.username)
        await bot.send_message(ADMIN_ID, 
                               f'New user!\n'
                               f'id: {message.from_user.id}\n'
                               f'first_name: {message.from_user.first_name}\n'
                               f'user_name: {message.from_user.username}')
        await bot.session.close()
        await message.answer(f"👋 Привет, {message.from_user.first_name}\n"
                            "\n"
                            "Я твой помощник по 🌦 погоде и 💱 валютам.\n"
                            "Я могу показать актуальную информацию в любой момент\n"
                            "\n"
                            "📌 Доступные команды:\n"
                            "/weather – узнать погоду в твоём городе\n"
                            '/weatherweek - узнать погоду на 5 дней в твоём городе\n'
                            "/currency – курсы валют (USD, EUR, PLN)\n"
                            "/help – помощь и описание функций")
    else:
        await message.answer(f"👋 С возвращением, {message.from_user.first_name}!\n"
                            "\n"
                            "Я слежу за 🌦 погодой и 💱 курсами валют,\n"
                            "чтобы у тебя всегда была свежая инфа под рукой\n"
                            '\n'
                            "📌 Доступные команды:\n"
                            "/weather – узнать погоду в твоём городе\n"
                            '/weatherweek - узнать погоду на 5 дней в твоём городе\n'
                            "/change_city - изменить город для прогноза погоды\n"  
                            "/currency – курсы валют (USD, EUR, PLN)\n"
                            "/change_currency - изменить основную валюту\n"  
                            "/help – помощь и описание функций")


@router.message(F.text.in_(['/weather_week', '/weather']))
async def weather_forecast(message: Message, state: FSMContext):
    weather = {'/weather_week': 
                {'validkey': 'weatherweek_daily_count',
                'count': 'weatherweek_daily_count',
                'limit': 3},

                '/weather':
                {'validkey': 'weather_daily_count',
                'count': 'weather_daily_count',
                'limit': 10}}
    if message.text == '🌦 Погода':
        key = '/weather'
    elif message.text == '☀️Погода на 5 дней':
        key = '/weather_week'
    else:
        key = message.text
    limit = weather[key]['limit']
    attempts_fromdb = await validation(message.from_user.id, weather[key]['validkey'])
    if attempts_fromdb >= limit:
        await (message.answer("🌤 Кажется, сегодня вы уже всё выяснили про нынешнюю погоду😊\n"
                    "Лимит запросов исчерпан — приходите завтра, узнаем, что готовит небо!")if key == '/weather' else message.answer(
                              "🌤 Кажется, сегодня вы уже всё выяснили про погоду на пять дней😊\n"
                    "Лимит запросов исчерпан — приходите завтра, узнаем, что готовит небо!"
                    ))
        return
    if await validation(message.from_user.id, 'cityandcoords') is None:
        await message.answer("❌ Упс, я пока не знаю, где ты живёшь.\n"  
                            "Введи свой город 🌆, и в следующий раз я смогу подсказать тебе погоду одним движением!")
        await state.set_state(Register.city)
    else:
        await message.answer('⏳ Подождите...')
        city = await validation(message.from_user.id, 'cityandcoords')
        result = await (get_weatherweek(city) if key == '/weather_week' else get_weather(city))
        await (message.answer("\n".join(result)) if key == '/weather_week' else message.answer(result))
        await daily_count(message.from_user.id, weather[key]['count'])
        attempts = (limit-1)-attempts_fromdb
        if attempts != 0:
            await (message.answer(f'☁️ Осталось всего {attempts} запрос(ов) узнать погоду на пять дней сегодня!\n'
                                  "Используйте их с умом 😊")if key == '/weatherweek' else message.answer(
                                  f'☁️ Осталось всего {attempts} запрос(ов) узнать нынешнюю погоду сегодня!\n'
                                  "Используйте их с умом 😊"))
        else:
            await (message.answer(f'☁️ Осталось всего {attempts} запрос(ов) узнать погоду на пять дней сегодня!\n'
                            "Приходите завтра 😊") if key == '/weatherweek' else message.answer(
                                 f'☁️ Осталось всего {attempts} запрос(ов) узнать нынешнюю погоду сегодня!\n'
                            "Приходите завтра 😊"
                            ))


@router.message(Command('change_city'))
async def change_city(message:Message, state:FSMContext):
    current_city = await validation(message.from_user.id, 'cityandcoords')
    if current_city is None:
        await message.answer("❌ Упс, я пока не знаю, где ты живёшь.\n"  
                            "Введи свой город 🌆, и в следующий раз я смогу подсказать тебе погоду одним движением!")
        await state.set_state(Register.city)
    else:
        city_data = json.loads(current_city)
        city = str(city_data['city'])
        await message.answer(f'🏢 Ваш нынешний город: {city}\n'
                        '🚀 Введите новый город, и я телепортируюсь туда прогнозом погоды!', reply_markup=stop_operation)
        await state.set_state(Register.city)


@router.message(F.text.in_(['🌦 Погода', '☀️Погода на 5 дней',
                            '💱 Курс валют', '🏠 Главное меню', '🛑Прервать операцию']))
async def back_to_mwc(message:Message, state:FSMContext):
    if message.text == '🌦 Погода' or message.text == '☀️Погода на 5 дней':
        await weather_forecast(message, state) 
    elif message.text == '💱 Курс валют':
        await currency(message)
    elif message.text == "🏠 Главное меню":
        await reg_user(message)    
    elif message.text == '🛑Прервать операцию':
        await state.clear()
        await message.answer("❌ Операция прервана", reply_markup=None)
        await reg_user(message)

#COMMANDS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
#COMMANDS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
#COMMANDS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼




# CALLBACKS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# CALLBACKS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# CALLBACKS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽

@router.callback_query(F.data.startswith('set_city'))
async def location(callback:CallbackQuery, state:FSMContext):
    try:
        _, lat, lon, city_name = callback.data.split(":")
        json_for_db = {'city': city_name,
                       'lat': lat,
                       'lon': lon}
        await save_city_and_coords(callback.from_user.id, json_for_db)
        await callback.message.edit_text(text="🥳Успешно!",reply_markup=None)
        await callback.message.answer(text='🔥Теперь ваш город сохранён.Что будем делать дальше?', reply_markup=keyboard_of_abil)
    finally:
        await state.clear()

#CALLBACKS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
#CALLBACKS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
#CALLBACKS🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼




class Register(StatesGroup):
    city = State()

@router.message(Register.city)
async def reg(message: Message, state:FSMContext):
    city = message.text
    if city[0] == '/':
        await message.answer('Enter the city name, not command/Введите название города, не команду')
        return
    if len(city) > 50:
        await message.answer('Слишком длинно')
        await message.answer('🌍Укажи свой существующий город,\n'
                            "чтобы я мог показывать точный прогноз погоды:")
        return
    try:
        cities = await find_city(city)
        keyboard = await build_city_keyboard(cities)
        await message.answer('🌍Выберите город из возможных: ', reply_markup=keyboard)
    except Exception:
        await message.answer('No such city')
    finally:
        await state.clear()




# WEATHER_FUNCTIONS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# WEATHER_FUNCTIONS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽
# WEATHER_FUNCTIONS 🔽🔽🔽🔽🔽🔽🔽🔽🔽🔽

async def get_weather(city):
    url = 'https://api.openweathermap.org/data/2.5/weather'
    try:
        data = await get_weather_forecast(url, city)
        sunset = datetime.fromtimestamp(data[-1]).strftime("%H:%M")
        sunrise = datetime.fromtimestamp(data[-2]).strftime("%H:%M")
        return (f"🌍 Город: {data[0]}, {data[1]}\n"
        f"🌡 Температура: {data[4]}°C (ощущается как {data[5]}°C)\n"
        f'📉 Минимальная: {data[2]}°C / Максимальная: {data[3]}°C\n'
        f'☁️ Погода: {data[6]}\n'
        f'💨 Ветер: {data[8]} м/с\n'
        f'💧 Влажность: {data[10]}%\n'
        f'☁️ Облачность: {data[12]}%\n'
        f'🌅 Восход солнца: {sunrise}\n 🌇 Закат: {sunset}'
        )
    except Exception as ex:
        print(ex)
        return 'Error, No such key'


async def get_weatherweek(city):
    url = 'https://api.openweathermap.org/data/2.5/forecast'
    try:
        data_dict = await get_weatherweek_forecast(url, city)
        result = [f'🌍 Город: {data_dict['location'][0]}, {data_dict['location'][1]}\n'
                  f'━━━━━━━━━━━━━━━━━━']
        for key, value in data_dict.items():
            if key == 'location':
                break
            days_ru = {
                "Monday": "Пн",
                "Tuesday": "Вт",
                "Wednesday": "Ср",
                "Thursday": "Чт",
                "Friday": "Пт",
                "Saturday": "Сб",
                "Sunday": "Вс",}
            
            months_ru = {
                1: "Января", 2: "Февраля", 3: "Марта", 4: "Апреля",
                5: "Мая", 6: "Июня", 7: "Июля", 8: "Августа",
                9: "Сентября", 10: "Октября", 11: "Ноября", 12: "Декабря"}

            date_str = str(key)
            day_str = datetime.strptime(date_str, "%Y-%m-%d")
            month, day = months_ru[day_str.month], day_str.day
            day_name = day_str.strftime('%A')


            result.append(
                        f"📅 {days_ru[day_name]}, {day} {month}\n"
                        f"• 🌡 Темп: {value['main']['temp']}°C (ощущается как {value['main']['feels_like']}°C)\n"
                        f"• 💧 Влажность: {value['main']['humidity']}%\n"
                        f"• 🌬 Ветер: {value['wind']['speed']} м/с, ↙ {value['wind']['deg']}°\n"
                        f"• 🌤 Облачность: {value['clouds']['all']}%\n"
                        f"• ⛅ Погода: {value['weather'][0]['description']}\n"
                        f"• 🌧 Осадки: {value.get('rain', {}).get('3h', 0)} мм\n"
                        f"━━━━━━━━━━━━━━━━━━"
            )
        return result
    except Exception as ex:
        print(ex)
        return 'Error, No such key'
    
    
async def APIrequest(city):
    city_data = json.loads(city)
    name = city_data['city']
    lat = float(city_data['lat'])
    lon = float(city_data['lon'])
    params = {
        "q": name,
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }
    return params

async def get_weather_forecast(url, city):
    params = await APIrequest(city)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if resp.status == 200: 
                inf = [
                    data["name"], 
                    data["sys"]["country"],
                    data["main"]["temp_min"],
                    data["main"]["temp_max"], 
                    data["main"]["temp"],
                    data["main"]["feels_like"],
                    data["weather"][0]["description"],
                    data["weather"][0]["icon"],
                    data["wind"]["speed"],
                    data["wind"].get("deg"),
                    data["main"]["humidity"],
                    data["main"]["pressure"],
                    data.get("clouds", {}).get("all"),
                    data["sys"]["sunrise"],
                    data["sys"]["sunset"]
                ]
                return inf

async def find_city(city_name):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city_name,
        "limit": 5,
        "appid": API_KEY,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            cities = [[i.get('local_names', {}).get('ru', i['name']),
                            i['country'], 
                            i.get('state'), 
                            i['lat'], i['lon']] for i in data]
            return cities
        
async def get_weatherweek_forecast(url, city):
    params = await APIrequest(city)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            dictio = {}
            for i in data['list']:
                date = i['dt_txt'].split()[0]
                dictio[date] = i
            dictio['location'] = [data['city']['name'], data['city']['country']]
            
            return dictio

# WEATHER_FUNCTIONS 🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
# WEATHER_FUNCTIONS 🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼
# WEATHER_FUNCTIONS 🔼🔼🔼🔼🔼🔼🔼🔼🔼🔼