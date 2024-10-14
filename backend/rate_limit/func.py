## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import json
import time
import aiofiles
import asyncio
import logging

## third-party imports
from fastapi import HTTPException, status

## custom imports
from constants import RATE_LIMIT_DATA_DIR, MAX_REQUESTS_PER_EMAIL, MAX_REQUESTS_PER_ID, RATE_LIMIT_WINDOW

from auth.util import get_secure_path

async def cleanup_old_rate_limit_files():
    current_time = time.time()
    for filename in os.listdir(RATE_LIMIT_DATA_DIR):
        file_path = os.path.join(RATE_LIMIT_DATA_DIR, filename)
        if(os.path.isfile(file_path)):
            file_mod_time = os.path.getmtime(file_path)
            if(current_time - file_mod_time > RATE_LIMIT_WINDOW * 2):  ## Remove files older than twice the rate limit window
                try:
                    await asyncio.to_thread(os.remove, file_path)
                except Exception as e:
                    logging.error(f"Error removing old rate limit file {file_path}: {e}")


async def rate_limit(email: str, id: str) -> None:
    if(not os.path.exists(RATE_LIMIT_DATA_DIR)):
        await asyncio.to_thread(os.makedirs, RATE_LIMIT_DATA_DIR)

    async with asyncio.Lock(): 
        email_data = await load_rate_limit_data(email, is_email=True)
        await check_and_update_rate_limit(email_data, MAX_REQUESTS_PER_EMAIL)

        id_data = await load_rate_limit_data(id, is_email=False)
        await check_and_update_rate_limit(id_data, MAX_REQUESTS_PER_ID)

        await save_rate_limit_data(email, is_email=True, data=email_data)
        await save_rate_limit_data(id, is_email=False, data=id_data)


async def load_rate_limit_data(email_or_id:str, is_email:bool) -> dict:
    directory = RATE_LIMIT_DATA_DIR
    prefix = "email_" if is_email else "id_"
    filename = f"{prefix}{email_or_id}.json"
    file_path = await get_secure_path(directory, filename)

    try:
        async with aiofiles.open(file_path, 'r') as f:
            return json.loads(await f.read())
        
    except FileNotFoundError:
        return {"requests": [], "blocked_until": None}


async def save_rate_limit_data(email_or_id:str, is_email:bool, data:dict) -> None:

    directory = RATE_LIMIT_DATA_DIR
    prefix = "email_" if is_email else "id_"
    filename = f"{prefix}{email_or_id}.json"
    file_path = await get_secure_path(directory, filename)

    async with aiofiles.open(file_path, 'w') as f:
        json.dump(data, f)


async def check_and_update_rate_limit(data:dict, max_requests:int) -> None:
    current_time = time.time()

    data['requests'] = [req for req in data['requests'] if current_time - req < RATE_LIMIT_WINDOW]

    if(data['blocked_until'] and current_time < data['blocked_until']):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                            detail="Rate limit exceeded. Please try again later.")

    if(len(data['requests']) >= max_requests):
        data['blocked_until'] = current_time + RATE_LIMIT_WINDOW
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                            detail="Rate limit exceeded. Please try again later.")

    data['requests'].append(current_time)

async def periodic_cleanup():
    while True:
        await asyncio.sleep(RATE_LIMIT_WINDOW)
        await asyncio.to_thread(cleanup_old_rate_limit_files)