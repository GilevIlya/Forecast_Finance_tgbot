import asyncpg
import json
from config import CONNECTION

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

async def weather_forallusers_to0_db():
    async with pool.acquire() as conn:
        tozero = 'UPDATE clients SET weather_daily_count = 0, weatherweek_daily_count = 0'
        await conn.execute(tozero)