from dotenv import load_dotenv, find_dotenv

import os
import asyncpg
import json
import aiohttp
import asyncio

find_path = find_dotenv()
load_dotenv(find_path)

CONNECTION = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST")
}

async def create_pool():
    global pool
    pool = await asyncpg.create_pool(**CONNECTION)

async def close_pool():
    await pool.close()

async def validation(id, key):
    async with pool.acquire() as conn:
        valid = f"SELECT {key} FROM clients WHERE id=$1"
        return await conn.fetchval(valid, id)

async def registration(id, first_name, username, city=None):
    async with pool.acquire() as conn:
        await conn.execute("""INSERT INTO clients (id, first_name, username, cityandcoords)
                        VALUES ($1, $2, $3, $4)""",id, first_name, username, city)

async def daily_count(id, key):
    async with pool.acquire() as conn:
        upd = f"UPDATE clients SET {key}={key}+1 WHERE id = ($1)"
        await conn.execute(upd, id)
    
async def save_city_and_coords(id, city_and_coords):
    async with pool.acquire() as conn:
        update = "UPDATE clients SET cityandcoords = $1 WHERE id = $2"
        jsonfile = json.dumps(city_and_coords)
        await conn.execute(update, jsonfile, id)

async def save_currency(id, cur):
    async with pool.acquire() as conn:
        update = 'UPDATE clients SET currency = $1 WHERE id = $2'
        await conn.execute(update, cur, id)

async def reset_weather_currency_at_midnight_db():
    async with pool.acquire() as conn:
        tozero = """UPDATE clients SET 
        weather_daily_count = 0, weatherweek_daily_count = 0,
        currency_count = 0"""
        await conn.execute(tozero)

async def update_db_currency_data(final_data):
    async with pool.acquire() as conn:
        values = [(base, json.dumps(targets)) for base, targets in final_data.items()]
        await conn.executemany("UPDATE currency_table SET currency = $2 WHERE currency_name = $1", values)

async def get_curr_from_db(user_curr):
    async with pool.acquire() as conn:
        result = await conn.fetch("SELECT * FROM currency_table WHERE currency_name = $1", user_curr)
        parsed_data = {record['currency_name']: json.loads(record['currency']) for record in result}
        return parsed_data