## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import asyncio

## third-party imports
from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse

## custom imports
from routes.models import EmailRequest, FeedbackEmailRequest

from auth.util import check_internal_request
from auth.func import check_if_admin_user

from email_util.common import send_email

from email_util.common import get_smtp_envs, send_email

from db.models import EmailAlertModel
from sqlalchemy.orm import Session
from db.base import get_db

router = APIRouter()

@router.post("/admin/send-email")
async def send_email_to_all(request: Request, email_request: EmailRequest, db: Session = Depends(get_db), is_admin:bool = Depends(check_if_admin_user)):

    await check_internal_request(request)

    if(not is_admin):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"message": "You are not authorized to send emails."})
    
    try:
        recipients = db.query(EmailAlertModel.email).all()
        smtp_envs = await get_smtp_envs()
        _, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, _ = smtp_envs
        
        tasks = [
            send_email(
                subject=email_request.subject,
                body=email_request.body,
                to_email=recipient.email,
                attachment_path=None,
                from_email=FROM_EMAIL,
                smtp_server=SMTP_SERVER,
                smtp_port=SMTP_PORT,
                smtp_user=SMTP_USER,
                smtp_password=SMTP_PASSWORD
            )
            for recipient in recipients
        ]
        await asyncio.gather(*tasks)
        
        return {"message": "Emails sent to all users successfully."}
    
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": f"An error occurred: {str(e)}"})

@router.post("/send-feedback-email")
async def send_feedback_email(request: Request, feedback:FeedbackEmailRequest):

    await check_internal_request(request)
    
    try:
        smtp_envs = await get_smtp_envs()
        _, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, _ = smtp_envs
        
        subject = "Feedback from Kakusui User"
        body = f"User Email: {feedback.email}\n\nFeedback: {feedback.text}"
        
        await send_email(
            subject=subject,
            body=body,
            to_email="support@kakusui.org",
            attachment_path=None,
            from_email=FROM_EMAIL,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            smtp_user=SMTP_USER,
            smtp_password=SMTP_PASSWORD
        )
        
        return {"message": "Feedback email sent successfully."}
    
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": f"An error occurred: {str(e)}"})
