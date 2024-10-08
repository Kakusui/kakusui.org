## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import asyncio
import aiofiles
import json
import string
import secrets
from pathlib import Path

from datetime import datetime, timedelta

## custom modules
from constants import VERIFICATION_EXPIRATION_MINUTES, VERIFICATION_DATA_DIR

from email_util.common import send_email, get_smtp_envs

from auth.util import get_secure_filename

def generate_verification_code() -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(6))

async def save_verification_data(email:str, code:str) -> None:
    expiration_time = datetime.now() + timedelta(minutes=VERIFICATION_EXPIRATION_MINUTES)
    data = {
        "code": code,
        "expiration": expiration_time.isoformat()
    }
    
    if(not os.path.exists(VERIFICATION_DATA_DIR)):
        await asyncio.to_thread(os.makedirs, VERIFICATION_DATA_DIR)

    secure_email = await get_secure_filename(email)
    file_path = Path(VERIFICATION_DATA_DIR) / f"{secure_email}.json"
    file_path = file_path.resolve()

    if(not file_path.is_relative_to(Path(VERIFICATION_DATA_DIR))):
        raise ValueError("Invalid email format")

    async with aiofiles.open(file_path, "w") as f:
        await f.write(json.dumps(data))

async def get_verification_data(email:str) -> dict | None:
    try:
        secure_email = await get_secure_filename(email)
        file_path = Path(VERIFICATION_DATA_DIR) / f"{secure_email}.json"
        file_path = file_path.resolve()

        if(not file_path.is_relative_to(Path(VERIFICATION_DATA_DIR))):
            raise ValueError("Invalid email format")

        async with aiofiles.open(file_path, "r") as f:
            data = json.loads(await f.read())
        return data
    
    except FileNotFoundError:
        return None

async def remove_verification_data(email:str) -> None:
    try:
        secure_email = await get_secure_filename(email)
        file_path = Path(VERIFICATION_DATA_DIR) / f"{secure_email}.json"
        file_path = file_path.resolve()

        if(not file_path.is_relative_to(Path(VERIFICATION_DATA_DIR))):
            raise ValueError("Invalid email format")

        ## Securely overwrite the file before deletion
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(os.urandom(1024))

        await asyncio.to_thread(os.remove, file_path)

    except FileNotFoundError:
        pass

async def send_verification_email(email:str, code:str) -> None:
    _, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, _ = await get_smtp_envs()

    subject = "Email Verification Code for https://kakusui.org"
    body = f"Your verification code is {code}"

    await send_email(subject=subject, body=body, to_email=email, attachment_path=None, from_email=FROM_EMAIL, smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, smtp_user=SMTP_USER, smtp_password=SMTP_PASSWORD)