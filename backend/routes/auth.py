## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
from datetime import timedelta, datetime

## third-party imports
from fastapi import APIRouter, HTTPException, Request, status, Cookie, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

## custom imports
from db.base import get_db
from db.models import User, EmailAlertModel


from routes.models import LoginModel, LoginToken, RegisterForEmailAlert, SendVerificationEmailRequest, VerifyEmailCodeRequest

from auth.func import verify_verification_code, create_access_token, create_refresh_token, func_verify_token, generate_verification_code, save_verification_data, send_verification_email, get_current_user
from auth.util import check_internal_request

from email_util.verification import get_verification_data, remove_verification_data

from rate_limit.func import rate_limit

from constants import TOKEN_EXPIRE_MINUTES, ADMIN_USER

import typing

router = APIRouter()

@router.post('/auth/check-email-registration')
async def check_email_registration(data:RegisterForEmailAlert, request:Request, db:Session = Depends(get_db)):
    origin = request.headers.get('origin')

    check_internal_request(origin)

    try:
        existing_user = db.query(User).filter(User.email == data.email).first()
        
        if(existing_user):
            return JSONResponse(status_code=status.HTTP_200_OK, content={"registered":True})
        else:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"registered":False})

    finally:
        db.close()

@router.post("/auth/login", response_model=LoginToken)
def login(data:LoginModel, request:Request, db:Session = Depends(get_db)) -> typing.Dict[str, str]:
    
    """
    
    Login endpoint for the API

    Args:
    data (LoginModel): The data required to login

    Returns:
    typing.Dict[str, str]: The access token and token type

    """

    origin = request.headers.get('origin')

    check_internal_request(origin)


    try:
        existing_user = db.query(User).filter(User.email == data.email).first()
        if(not existing_user):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if(not verify_verification_code(data.email, data.verification_code)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or verification code",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": data.email}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        refresh_token = create_refresh_token(
            data={"sub": data.email}, expires_delta=refresh_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

    finally:
        db.close()

@router.post("/auth/signup")
async def signup(data:LoginModel, request:Request, db:Session = Depends(get_db)) -> JSONResponse:

    origin = request.headers.get('origin')

    check_internal_request(origin)

    try:

        existing_user = db.query(User).filter(User.email == data.email).first()


        if(existing_user):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Email already registered."})

        if(not verify_verification_code(data.email, data.verification_code)):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "Invalid email or verification code"})

        new_user = User(email=data.email)
        db.add(new_user)
        db.commit()

        access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": data.email}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        refresh_token = create_refresh_token(
            data={"sub": data.email}, expires_delta=refresh_token_expires
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "message": "User successfully registered.",
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token
        })

    except Exception as e:
        db.rollback()
        print(f"Error during signup: {str(e)}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "An error occurred during signup."})

    finally:
        db.close()

@router.post("/auth/refresh-access-token", response_model=LoginToken)
def refresh_token(request:Request, refresh_token: str = Cookie(None)) -> JSONResponse:
    
    """

    Refresh the access token using the refresh token

    Args:
    refresh_token (str): The refresh token

    Returns:
    typing.Dict[str, str]: The access token and token type

    """

    origin = request.headers.get('origin')

    check_internal_request(origin)

    if(refresh_token is None):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided")

    token_data = func_verify_token(refresh_token)
    access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": token_data.email}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    new_refresh_token = create_refresh_token(
        data={"sub": token_data.email}, expires_delta=refresh_token_expires
    )

    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=TOKEN_EXPIRE_MINUTES
    )
    return response
    

@router.post("/auth/send-verification-email")
async def send_verification_email_endpoint(request_data: SendVerificationEmailRequest, request: Request, db: Session = Depends(get_db)):
    origin = request.headers.get('origin')

    check_internal_request(origin)
    
    email = request_data.email
    client_id = request_data.clientID

    try:
        existing_user = db.query(User).filter(User.email == email).first()
        
        if(not existing_user):
            try:
                rate_limit(email, client_id)
            except HTTPException as e:
                return JSONResponse(status_code=e.status_code, content={"message": e.detail})
        
        verification_code = generate_verification_code()
        save_verification_data(email, verification_code)
        send_verification_email(email, verification_code)

        if(existing_user):
            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Verification email sent successfully for login."})
        else:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Verification email sent successfully for signup."})
    
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "An error occurred while sending the verification email."})

@router.post("/auth/verify-token")
async def verify_token_endpoint(request: Request):

    origin = request.headers.get('origin')

    check_internal_request(origin)

    auth_header = request.headers.get("Authorization")
    
    if(not auth_header or not auth_header.startswith("Bearer ")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    
    token = auth_header.split(" ")[1]

    try:
        token_data = func_verify_token(token)
        return {"valid": True, "email": token_data.email}
    
    except HTTPException as e:
        return {"valid": False, "detail": str(e.detail)}

@router.post("/auth/check-if-admin-user")
async def check_admin(request: Request, current_user:str = Depends(get_current_user)):
    origin = request.headers.get('origin')

    check_internal_request(origin)

    is_admin = current_user == ADMIN_USER

    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": is_admin})

@router.post("/auth/landing-verify-code", response_model=LoginToken)
async def landing_verify_code_endpoint(request_data:VerifyEmailCodeRequest, request:Request, db: Session = Depends(get_db)):
    origin = request.headers.get('origin')

    check_internal_request(origin)

    email = request_data.email
    submitted_code = request_data.code

    try:
        verification_data = get_verification_data(email)
        if(not verification_data):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Verification code not found or expired."})

        stored_code = verification_data["code"]
        expiration_time = datetime.fromisoformat(verification_data["expiration"])

        if(datetime.now() > expiration_time):
            remove_verification_data(email)
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Verification code has expired."})

        if(submitted_code != stored_code):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Invalid verification code."})

        existing_email_alert = db.query(EmailAlertModel).filter(EmailAlertModel.email == email).first()
        if(existing_email_alert):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Email already registered for alerts."})

        new_email_alert = EmailAlertModel(email=email)
        db.add(new_email_alert)
        db.commit()
        
        remove_verification_data(email)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Email successfully verified and registered for alerts.", "token_type": "bearer"})
    
    except Exception as e:
        db.rollback()
        print(f"Error verifying landing page email code: {str(e)}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "An error occurred while verifying the email code."})