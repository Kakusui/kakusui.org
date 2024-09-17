## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import json
import random
import string

from datetime import datetime, timedelta

## custom modules
from constants import VERIFICATION_EXPIRATION_MINUTES, VERIFICATION_DATA_DIR

from email_util.common import send_email, get_smtp_envs

from auth.util import get_secure_filename

def generate_verification_code() -> str:
    return ''.join(random.choices(string.digits, k=6))

def save_verification_data(email:str, code:str) -> None:
    expiration_time = datetime.now() + timedelta(minutes=VERIFICATION_EXPIRATION_MINUTES)
    data = {
        "code": code,
        "expiration": expiration_time.isoformat()
    }
    
    if(not os.path.exists(VERIFICATION_DATA_DIR)):
        os.makedirs(VERIFICATION_DATA_DIR)

    secure_email = get_secure_filename(email)

    with open(f"{VERIFICATION_DATA_DIR}/{secure_email}.json", "w") as f:
        json.dump(data, f)

def get_verification_data(email:str) -> dict | None:
    try:
        secure_email = get_secure_filename(email)
        with open(f"{VERIFICATION_DATA_DIR}/{secure_email}.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None

def remove_verification_data(email:str) -> None:
    try:
        secure_email = get_secure_filename(email)
        os.remove(f"{VERIFICATION_DATA_DIR}/{secure_email}.json")
    except FileNotFoundError:
        pass

def send_verification_email(email:str, code:str) -> None:
    _, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, _ = get_smtp_envs()

    subject = "Email Verification Code for Kakusui.org"
    body = f"Your verification code is {code}"

    send_email(subject=subject, body=body, to_email=email, attachment_path=None, from_email=FROM_EMAIL, smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, smtp_user=SMTP_USER, smtp_password=SMTP_PASSWORD)
