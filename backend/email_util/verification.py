## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## custom modules
from constants import VERIFICATION_EXPIRATION_MINUTES
from email_util.common import send_email, get_smtp_envs
from auth.verification import (
    get_verification_data as load_verification_data,
    remove_verification_data as delete_verification_data,
    save_verification_data as store_verification_data,
)

import secrets
import string

def generate_verification_code() -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(6))

async def save_verification_data(email: str, code: str) -> None:
    store_verification_data(email, code)

async def get_verification_data(email: str) -> dict | None:
    return load_verification_data(email)

async def remove_verification_data(email: str) -> None:
    delete_verification_data(email)

async def send_verification_email(email: str, code: str) -> None:
    _, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, _ = await get_smtp_envs()

    subject = "Email Verification Code for https://kakusui.org"
    body = f"Your verification code is {code}. Note that this code will expire in {VERIFICATION_EXPIRATION_MINUTES} minutes. Do not share this code with others. No one from Kakusui LLC will ask you for this code."

    await send_email(subject=subject, body=body, to_email=email, attachment_path=None, from_email=FROM_EMAIL, smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, smtp_user=SMTP_USER, smtp_password=SMTP_PASSWORD)
