from dotenv import load_dotenv, find_dotenv
from redis_client import rds_client
import os
import asyncpg
import json

find_path = find_dotenv()
load_dotenv(find_path)

CONNECTION = {
    "host": "postgres",
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
    "port": 5432
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

async def update_db_currency_data(json_final_data):
    async with pool.acquire() as conn:
        await conn.execute("""INSERT INTO public.currency_table (id, currency_value, currency_key)
                            VALUES (1, $1, $2)
                            ON CONFLICT (id) 
                            DO UPDATE SET 
                                currency_value = EXCLUDED.currency_value,
                                currency_key = EXCLUDED.currency_key;""", json_final_data, 'currency_data')
        # await conn.execute("UPDATE currency_table SET currency_value = $2 WHERE currency_key = $1", 'currency_data', json_final_data)

async def get_curr_from_db():
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT * FROM currency_table WHERE currency_key = $1", 'currency_data')
        return result

async def filling_redis_on_start():
    get_data = await get_curr_from_db()
    rds_client.set('currency_data', get_data, ex=10800)