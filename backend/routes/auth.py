## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import asyncio
from datetime import timedelta

import logging

## third-party imports
from fastapi import APIRouter, HTTPException, Request, status, Cookie, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

## custom imports
from db.base import get_db
from db.models import User, EmailAlertModel

from routes.models import LoginModel, LoginToken, RegisterForEmailAlert, SendVerificationEmailRequest, VerifyEmailCodeRequest, GoogleLoginRequest

from auth.func import verify_verification_code, create_access_token, create_refresh_token, func_verify_token, generate_verification_code, save_verification_data, send_verification_email, get_current_user
from auth.throttle import (
    enforce_google_login_limits,
    enforce_otp_issue_limits_after_verification,
    enforce_otp_issue_source_limit,
    enforce_otp_verify_limits,
)
from auth.google import verify_google_id_token
from auth.verification import VerificationAttemptsExceeded, canonicalize_email
from routes.turnstile import verify_turnstile_token
from auth.util import check_internal_request

from constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ADMIN_USER,
    GOOGLE_CLIENT_ID,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

router = APIRouter()


def _find_user_by_email(db: Session, email: str) -> User | None:
    normalized_email = canonicalize_email(email)
    return db.query(User).filter(User.email == normalized_email).first()


def _set_refresh_cookie(response: JSONResponse, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

@router.post('/auth/google-login')
async def google_login(
    request_data: GoogleLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    await check_internal_request(request)
    enforce_google_login_limits(request)
    try:
        idinfo = await asyncio.to_thread(
            verify_google_id_token,
            request_data.token,
            GOOGLE_CLIENT_ID,
        )

        if(
            idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']
            or not idinfo.get("email_verified")
        ):
            raise ValueError('Wrong issuer.')

        email = canonicalize_email(idinfo['email'])
        
        user = _find_user_by_email(db, email)
        if(not user):
            user = User(email=email)
            db.add(user)
            db.commit()
        elif(not user.is_active):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        token_email = user.email

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(
            data={"sub": token_email}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = await create_refresh_token(
            data={"sub": token_email}, expires_delta=refresh_token_expires
        )

        response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
        _set_refresh_cookie(response, refresh_token)
        return response

    except ValueError:
        raise HTTPException(status_code=400, detail='Invalid token')
    finally:
        db.close()

@router.post('/auth/check-email-registration')
async def check_email_registration(data:RegisterForEmailAlert, request:Request):

    await check_internal_request(request)
    del data
    return JSONResponse(status_code=status.HTTP_200_OK, content={"accepted": True})

@router.post("/auth/login", response_model=LoginToken)
async def login(data:LoginModel, request:Request, db:Session = Depends(get_db)) -> JSONResponse:
    
    """
    
    Login endpoint for the API

    Args:
    data (LoginModel): The data required to login

    Returns:
    typing.Dict[str, str]: The access token and token type

    """

    await check_internal_request(request)
    enforce_otp_verify_limits(request, data.email)

    try:
        try:
            valid_code = await verify_verification_code(data.email, data.verification_code)
        except VerificationAttemptsExceeded as error:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(error),
                headers={"Retry-After": "3600"},
            )

        if(not valid_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or verification code",
                headers={"WWW-Authenticate": "Bearer"},
            )

        existing_user = _find_user_by_email(db, data.email)
        if(not existing_user or not existing_user.is_active):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or verification code",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(
            data={"sub": existing_user.email}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = await create_refresh_token(
            data={"sub": existing_user.email}, expires_delta=refresh_token_expires
        )

        response = JSONResponse({
            "access_token": access_token,
            "token_type": "bearer",
        })
        _set_refresh_cookie(response, refresh_token)
        return response

    finally:
        db.close()

@router.post("/auth/signup")
async def signup(data:LoginModel, request:Request, db:Session = Depends(get_db)) -> JSONResponse:

    await check_internal_request(request)
    enforce_otp_verify_limits(request, data.email)

    try:
        try:
            verification_result = await verify_verification_code(data.email, data.verification_code)
        except VerificationAttemptsExceeded as error:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"message": str(error)},
                headers={"Retry-After": "3600"},
            )
        if(not verification_result):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Invalid email or verification code"})

        normalized_email = canonicalize_email(data.email)
        existing_user = _find_user_by_email(db, normalized_email)
        if(existing_user):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Unable to create account."})

        new_user = User(email=normalized_email)
        db.add(new_user)
        db.commit()

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(
            data={"sub": normalized_email}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = await create_refresh_token(
            data={"sub": normalized_email}, expires_delta=refresh_token_expires
        )

        response = JSONResponse(status_code=status.HTTP_200_OK, content={
            "message": "User successfully registered.",
            "access_token": access_token,
            "token_type": "bearer"
        })
        _set_refresh_cookie(response, refresh_token)
        return response

    except Exception as e:
        db.rollback()
        logging.error(f"Error during signup: {str(e)}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "An error occurred during signup."})

    finally:
        db.close()

@router.post("/auth/refresh-access-token", response_model=LoginToken)
async def refresh_token(
    request:Request,
    refresh_token: str = Cookie(None),
    db: Session = Depends(get_db),
) -> JSONResponse:
    
    """

    Refresh the access token using the refresh token

    Args:
    refresh_token (str): The refresh token

    Returns:
    typing.Dict[str, str]: The access token and token type

    """

    await check_internal_request(request)

    if(refresh_token is None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided")

    token_data = await func_verify_token(refresh_token, token_type="refresh")
    user = _find_user_by_email(db, token_data.email)
    if(user is None or not user.is_active):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    return response


@router.post("/auth/logout")
async def logout(request: Request) -> JSONResponse:
    await check_internal_request(request)
    response = JSONResponse(content={"message": "Logged out."})
    response.delete_cookie(
        key="refresh_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="none",
    )
    return response
    

@router.post("/auth/send-verification-email")
async def send_verification_email_endpoint(request_data: SendVerificationEmailRequest, request: Request):

    await check_internal_request(request)
    enforce_otp_issue_source_limit(request)
    await verify_turnstile_token(request_data.turnstile_token, request, "verification_email")
    
    email = canonicalize_email(request_data.email)

    try:
        enforce_otp_issue_limits_after_verification(email)
    except HTTPException as error:
        return JSONResponse(
            status_code=error.status_code,
            content={"message": error.detail},
            headers=error.headers,
        )

    try:
        verification_code = await generate_verification_code()
        try:
            await save_verification_data(email, verification_code)
        except VerificationAttemptsExceeded as error:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"message": str(error)},
                headers={"Retry-After": "3600"},
            )
        await send_verification_email(email, verification_code)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "If the address can receive mail, a verification code was sent."},
        )
    
    except Exception as e:
        logging.error(f"Error sending verification email: {str(e)}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "An error occurred while sending the verification email."})

@router.post("/auth/verify-token")
async def verify_token_endpoint(request: Request):

    await check_internal_request(request)

    auth_header = request.headers.get("Authorization")
    
    if(not auth_header or not auth_header.startswith("Bearer ")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    
    token = auth_header.split(" ")[1]

    try:
        token_data = await func_verify_token(token)
        return {"valid": True, "email": token_data.email}
    
    except HTTPException as e:
        return {"valid": False, "detail": str(e.detail)}

@router.post("/auth/check-if-admin-user")
async def check_admin(request: Request, current_user:str = Depends(get_current_user)):
    
    await check_internal_request(request)

    is_admin = (current_user == ADMIN_USER)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": is_admin})

@router.post("/auth/landing-verify-code", response_model=LoginToken)
async def landing_verify_code_endpoint(request_data:VerifyEmailCodeRequest, request:Request, db: Session = Depends(get_db)):

    await check_internal_request(request)

    email = canonicalize_email(request_data.email)
    submitted_code = request_data.code
    enforce_otp_verify_limits(request, email)

    try:
        try:
            valid_code = await verify_verification_code(email, submitted_code)
        except VerificationAttemptsExceeded as error:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"message": str(error)},
                headers={"Retry-After": "3600"},
            )

        if(not valid_code):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Invalid verification code."})

        existing_email_alert = db.query(EmailAlertModel).filter(EmailAlertModel.email == email).first()
        if(existing_email_alert):
            pass
            ## just don't register, but still return success

        else:
            new_email_alert = EmailAlertModel(email=email)
            db.add(new_email_alert)
            db.commit()
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Email successfully verified and registered for alerts.", "token_type": "bearer"})
    
    except Exception as e:
        db.rollback()
        logging.error(f"Error verifying landing page email code: {str(e)}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "An error occurred while verifying the email code."})
