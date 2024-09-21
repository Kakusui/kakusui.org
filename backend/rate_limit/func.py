## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import json
import time

## third-party imports
from fastapi import HTTPException, status

## custom imports
from constants import RATE_LIMIT_DATA_DIR, MAX_REQUESTS_PER_EMAIL, MAX_REQUESTS_PER_ID, RATE_LIMIT_WINDOW

from auth.util import get_secure_path


def rate_limit(email:str, id:str) -> None:

    if(not os.path.exists(RATE_LIMIT_DATA_DIR)):
        os.makedirs(RATE_LIMIT_DATA_DIR)

    email_data = load_rate_limit_data(email, is_email=True)
    check_and_update_rate_limit(email_data, MAX_REQUESTS_PER_EMAIL, "email")

    id_data = load_rate_limit_data(id, is_email=False)
    check_and_update_rate_limit(id_data, MAX_REQUESTS_PER_ID, "ID")

    save_rate_limit_data(email, is_email=True, data=email_data)
    save_rate_limit_data(id, is_email=False, data=id_data)

def load_rate_limit_data(email_or_id:str, is_email:bool) -> dict:
    directory = RATE_LIMIT_DATA_DIR
    prefix = "email_" if is_email else "id_"
    filename = f"{prefix}{email_or_id}.json"
    file_path = get_secure_path(directory, filename)

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
        
    except FileNotFoundError:
        return {"requests": [], "blocked_until": None}

def save_rate_limit_data(email_or_id:str, is_email:bool, data:dict) -> None:

    directory = RATE_LIMIT_DATA_DIR
    prefix = "email_" if is_email else "id_"
    filename = f"{prefix}{email_or_id}.json"
    file_path = get_secure_path(directory, filename)

    with open(file_path, 'w') as f:
        json.dump(data, f)

def check_and_update_rate_limit(data:dict, max_requests:int, limit_type:str) -> None:
    current_time = time.time()

    data['requests'] = [req for req in data['requests'] if current_time - req < RATE_LIMIT_WINDOW]

    if(data['blocked_until'] and current_time < data['blocked_until']):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Too many requests from this {limit_type}. Please try again later.")

    if(len(data['requests']) >= max_requests):
        data['blocked_until'] = current_time + RATE_LIMIT_WINDOW
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"Too many requests from this {limit_type}. Please try again later.")

    data['requests'].append(current_time)