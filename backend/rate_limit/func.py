## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import time
import asyncio
import logging

## third-party imports
from fastapi import HTTPException, status

## custom imports
from constants import MAX_REQUESTS_PER_EMAIL, MAX_REQUESTS_PER_ID, RATE_LIMIT_WINDOW

# In-memory storage for rate limit data
rate_limit_data = {}
rate_limit_lock = asyncio.Lock()

async def cleanup_old_rate_limit_data():
    current_time = time.time()
    removed_count = 0
    async with rate_limit_lock:
        for key in list(rate_limit_data.keys()):
            if(current_time - rate_limit_data[key]['last_update'] > RATE_LIMIT_WINDOW * 2):
                del rate_limit_data[key]
                removed_count += 1
    logging.info(f"Cleaned up {removed_count} expired rate limit entries")

async def rate_limit(email: str, id: str) -> None:
    async with rate_limit_lock:
        await check_and_update_rate_limit(f"email_{email}", MAX_REQUESTS_PER_EMAIL)
        await check_and_update_rate_limit(f"id_{id}", MAX_REQUESTS_PER_ID)

async def check_and_update_rate_limit(key: str, max_requests: int) -> None:
    current_time = time.time()

    if(key not in rate_limit_data):
        rate_limit_data[key] = {"requests": [], "blocked_until": None, "last_update": current_time}

    data = rate_limit_data[key]
    data['requests'] = [req for req in data['requests'] if current_time - req < RATE_LIMIT_WINDOW]
    data['last_update'] = current_time

    if(data['blocked_until'] and current_time < data['blocked_until']):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                            detail="Rate limit exceeded. Please try again later.")

    if(len(data['requests']) >= max_requests):
        data['blocked_until'] = current_time + RATE_LIMIT_WINDOW
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                            detail="Rate limit exceeded. Please try again later.")

    data['requests'].append(current_time)