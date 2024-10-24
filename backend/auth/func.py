## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import typing
import string
import secrets
from hmac import compare_digest

from datetime import datetime, timedelta, timezone

## third-party imports
from pydantic import EmailStr
from jwt import PyJWTError

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

## custom imports
from main import verification_data, verification_lock

from routes.models import TokenData

from email_util.common import send_email, get_smtp_envs

from constants import (
    ACCESS_TOKEN_SECRET,
    REFRESH_TOKEN_SECRET,
    TOKEN_ALGORITHM,
    ADMIN_USER,
    VERIFICATION_EXPIRATION_MINUTES,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    GEMINI_API_KEY,
    MAX_EMAIL_VERIFICATION_ATTEMPTS
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def create_access_token(data:dict, 
                        expires_delta:typing.Optional[timedelta]) -> str:

    """
    
    Create an access token with the given data and expiration time

    Args:
    data (dict): The data to encode into the token
    expires_delta (timedelta): The time until the token expires

    Returns:
    encoded_jwt (str): The encoded JWT token

    """

    to_encode = data.copy()

    if(expires_delta):
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET, algorithm=TOKEN_ALGORITHM) # type: ignore

    return encoded_jwt

async def create_refresh_token(data:dict, 
                         expires_delta:typing.Optional[timedelta]) -> str:

    """

    Create a refresh token with the given data and expiration time

    Args:
    data (dict): The data to encode into the token
    expires_delta (timedelta): The time until the token expires

    Returns:
    encoded_jwt (str): The encoded JWT token

    """

    to_encode = data.copy()

    if(expires_delta):
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=1)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm=TOKEN_ALGORITHM) # type: ignore
    return encoded_jwt

async def verify_verification_code(email:str, verification_code:str) -> bool:

    """

    Verify the given verification code for the given email

    Args:
    email (str): The email to verify
    verification_code (str): The verification code to verify

    Returns:

    bool: True if the verification code is valid, False otherwise

    """

    verification_data = await get_verification_data(email)
    if(not verification_data):
        return False
    
    stored_code = verification_data["code"]
    expiration_time = datetime.fromisoformat(verification_data["expiration"])
    attempts = verification_data.get("attempts", 0)
    
    if(datetime.now() > expiration_time):
        await remove_verification_data(email)
        return False
    
    if(attempts >= MAX_EMAIL_VERIFICATION_ATTEMPTS):
        await remove_verification_data(email)
        return False
    
    if(compare_digest(verification_code, stored_code)):
        await remove_verification_data(email)
        return True
    
    ## Increment attempts and save
    verification_data["attempts"] = attempts + 1
    await save_verification_data(email, verification_data["code"], verification_data)
    
    return False

async def func_verify_token(token:str) -> TokenData:

    """

    Verify the given token and return the data

    Args:    
    token (str): The token to verify

    Returns:
    TokenData: The data from the token

    """

    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=[TOKEN_ALGORITHM]) # type: ignore
        email:str = payload.get("sub")

        if(email is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return TokenData(email=email)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
async def get_current_user(token:str = Depends(oauth2_scheme)):

    """

    Get the current user from the given token

    Args:
    token (str): The token to get the user from

    Returns:
    str: The email of the user

    """

    if(not token):
        return ""

    try:
        token_data = await func_verify_token(token)
        return token_data.email
    
    except HTTPException as e:
        return ""

async def check_if_admin_user(current_user:str = Depends(get_current_user)):

    """

    Get the current active user

    Args:
    current_user (str): The current user

    Returns:
    str: The username of the user

    """

    is_admin = False

    if(current_user == ADMIN_USER):
        is_admin = True
        
    return is_admin

async def generate_verification_code() -> str:
    return ''.join(secrets.choice(string.digits) for _ in range(6))

async def save_verification_data(email: str, code: str, existing_data: dict | None = None) -> None:
    if(existing_data is None):
        expiration_time = datetime.now() + timedelta(minutes=VERIFICATION_EXPIRATION_MINUTES)
        data = {
            "code": code,
            "expiration": expiration_time.isoformat(),
            "attempts": 0
        }
    else:
        data = existing_data
        data["code"] = code

    async with verification_lock:
        verification_data[email] = data

async def get_verification_data(email: str) -> dict | None:
    async with verification_lock:
        return verification_data.get(email)

async def remove_verification_data(email: str) -> None:
    async with verification_lock:
        verification_data.pop(email, None)

async def send_verification_email(email:EmailStr, code:str) -> None:
    _, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, _ = await get_smtp_envs()

    subject = "Email Verification Code for https://kakusui.org"
    body = f"Your verification code is {code}. Do not share this code with anyone. Someone from Kakusui will never ask you for this code."

    await send_email(
        subject=subject, 
        body=body, 
        to_email=email, 
        attachment_path=None, 
        from_email=FROM_EMAIL, 
        smtp_server=SMTP_SERVER, 
        smtp_port=SMTP_PORT, 
        smtp_user=SMTP_USER, 
        smtp_password=SMTP_PASSWORD
    )

async def get_admin_api_key(llm_type:str) -> str | None: 
    if(llm_type == "openai"):
        return OPENAI_API_KEY
    elif(llm_type == "anthropic"):
        return ANTHROPIC_API_KEY
    elif(llm_type == "gemini"):
        return GEMINI_API_KEY
    else:
        return None

async def cleanup_expired_verification_data():
    current_time = datetime.now()
    async with verification_lock:
        for email in list(verification_data.keys()):
            data = verification_data[email]
            expiration_time = datetime.fromisoformat(data["expiration"])
            if current_time > expiration_time:
                del verification_data[email]
