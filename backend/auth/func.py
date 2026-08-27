## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import typing
import string
import secrets

from datetime import datetime, timedelta, timezone

## third-party imports
from pydantic import EmailStr
from jwt import PyJWTError

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from routes.models import TokenData
from auth.verification import (
    cleanup_expired_verification_data as cleanup_verification_data,
    get_verification_data as load_verification_data,
    remove_verification_data as delete_verification_data,
    save_verification_data as store_verification_data,
    verify_verification_code as verify_stored_verification_code,
)

from email_util.common import send_email, get_smtp_envs

from constants import (
    ACCESS_TOKEN_SECRET,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_SECRET,
    REFRESH_TOKEN_EXPIRE_DAYS,
    TOKEN_ALGORITHM,
    ADMIN_USER,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    GEMINI_API_KEY,
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
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "typ": "access"})
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
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "typ": "refresh"})
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

    return verify_stored_verification_code(email, verification_code)

async def func_verify_token(
    token:str,
    token_type:typing.Literal["access", "refresh"] = "access",
) -> TokenData:

    """

    Verify the given token and return the data

    Args:    
    token (str): The token to verify

    Returns:
    TokenData: The data from the token

    """

    try:
        secret = ACCESS_TOKEN_SECRET if token_type == "access" else REFRESH_TOKEN_SECRET
        payload = jwt.decode(
            token,
            secret,
            algorithms=[TOKEN_ALGORITHM],
            options={"require": ["exp", "sub"]},
        ) # type: ignore
        email = payload.get("sub")
        encoded_type = payload.get("typ")

        if(not isinstance(email, str) or not email):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        if(encoded_type is not None and encoded_type != token_type):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        # Legacy tokens remain valid only when the signing key itself proves
        # their type. With a shared key, an untyped refresh and access token are
        # cryptographically indistinguishable, so both must be invalidated.
        if(
            encoded_type is None
            and ACCESS_TOKEN_SECRET == REFRESH_TOKEN_SECRET
        ):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        
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
    
    except HTTPException:
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
    store_verification_data(email, code, existing_data)

async def get_verification_data(email: str) -> dict | None:
    return load_verification_data(email)

async def remove_verification_data(email: str) -> None:
    delete_verification_data(email)

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
    cleanup_verification_data()
