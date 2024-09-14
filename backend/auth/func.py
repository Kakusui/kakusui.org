## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import typing
import os
import json
import random
import string

from datetime import datetime, timedelta, timezone

## third-party imports
from jwt import PyJWTError

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

## custom imports
from routes.models import TokenData

from auth.util import get_secure_filename

from email_util.common import send_email, get_smtp_envs

from constants import ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET, TOKEN_ALGORITHM, ADMIN_USER, VERIFICATION_DATA_DIR, VERIFICATION_EXPIRATION_MINUTES, OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data:dict, 
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

def create_refresh_token(data:dict, 
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

def verify_verification_code(email: str, verification_code: str) -> bool:

    """

    Verify the given verification code for the given email

    Args:
    email (str): The email to verify
    verification_code (str): The verification code to verify

    Returns:

    bool: True if the verification code is valid, False otherwise

    """

    verification_data = get_verification_data(email)
    if(not verification_data):
        return False
    
    stored_code = verification_data["code"]
    expiration_time = datetime.fromisoformat(verification_data["expiration"])
    
    if(datetime.now() > expiration_time):
        return False
    
    remove_verification_data(email)
    
    return verification_code == stored_code

def func_verify_token(token:str) -> TokenData:

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
    
def get_current_user(token:str = Depends(oauth2_scheme)):

    """

    Get the current user from the given token

    Args:
    token (str): The token to get the user from

    Returns:
    str: The email of the user

    """

    try:
        token_data = func_verify_token(token)
        return token_data.email
    except HTTPException as e:
        raise e

def get_current_active_user(current_user:str = Depends(get_current_user)):

    """

    Get the current active user

    Args:
    current_user (str): The current user

    Returns:
    str: The username of the user

    """

    if(current_user != ADMIN_USER):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    return current_user

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

def get_admin_api_key(llm_type:str) -> str | None: 
    if(llm_type == "openai"):
        return OPENAI_API_KEY
    elif(llm_type == "anthropic"):
        return ANTHROPIC_API_KEY
    elif(llm_type == "gemini"):
        return GEMINI_API_KEY
    else:
        return None