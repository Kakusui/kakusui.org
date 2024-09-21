## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse

## custom imports
from routes.models import EmailRequest

from auth.util import check_internal_request
from auth.func import check_if_admin_user

from email_util.common import send_email

from email_util.common import get_smtp_envs, send_email

from db.models import EmailAlertModel
from sqlalchemy.orm import Session
from db.base import get_db

router = APIRouter()

@router.post("/admin/send-email")
async def send_email_to_all(request: Request, email_request: EmailRequest, db: Session = Depends(get_db), is_admin: bool = Depends(check_if_admin_user)):
    origin = request.headers.get('origin')
    check_internal_request(origin)
    
    try:
        recipients = db.query(EmailAlertModel.email).all()
        smtp_envs = get_smtp_envs()
        _, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, _ = smtp_envs
        
        for recipient in recipients:
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
        
        return {"message": "Emails sent to all users successfully."}
    
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": f"An error occurred: {str(e)}"})