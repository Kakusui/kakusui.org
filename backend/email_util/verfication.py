## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import json
import random
import string

from datetime import datetime, timedelta

## third-party imports
from fastapi import Request, status
from fastapi.responses import JSONResponse

from sqlalchemy.orm import sessionmaker, Session

## custom imports
from routes.models import VerifyEmailCodeRequest

from db.models import EmailAlertModel
from db.common import get_db

from constants import VERIFICATION_EXPIRATION_MINUTES, VERIFICATION_DATA_DIR

from email_util.common import send_email, get_smtp_envs

from auth.util import check_internal_request, get_secure_filename

async def verify_email_code_endpoint(request_data:VerifyEmailCodeRequest, request:Request, SessionLocal:sessionmaker):

    origin = request.headers.get('origin')

    check_internal_request(origin)

    email = request_data.email
    submitted_code = request_data.code

    db:Session = next(get_db(SessionLocal))

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
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Email successfully verified and registered for alerts."})
    
    except Exception as e:
        db.rollback()
        print(f"Error verifying email code: {str(e)}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "An error occurred while verifying the email code."})
    
    finally:
        db.close()

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
