## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## build-in imports
import typing
import os
import asyncio
import aiofiles

## third-party imports
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request, Body, status
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, select

## custom modules
from email_util.backup import perform_backup, decrypt_file, decompress_file, replace_sqlite_db
from email_util.common import send_email, get_smtp_envs

from db.base import engine, get_db
from db.models import EmailAlertModel, User

from auth.func import check_if_admin_user, get_current_user
from auth.util import check_internal_request

from constants import ENCRYPTION_KEY

from routes.models import EmailRequest

from main import maintenance_mode, maintenance_lock


router = APIRouter()

@router.post("/admin/db/send-email")
async def send_email_to_all(request: Request, email_request:EmailRequest, db: Session = Depends(get_db), is_admin:bool = Depends(check_if_admin_user)):

    await check_internal_request(request)

    if(not is_admin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this action.")
    
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


@router.post('/admin/db/force-backup')
async def force_backup(request:Request, db:Session = Depends(get_db), is_admin:bool = Depends(check_if_admin_user)):

    """

    Force a backup

    Args:
    current_user (str): The current user

    Returns:
    typing.Dict[str, str]: The result of the operation

    """

    await check_internal_request(request)

    if(not is_admin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this action.")

    await perform_backup(db)

    return {"message": "Backup started"}

@router.post("/admin/db/replace-database")
async def upload_backup(request:Request, file: UploadFile = File(...), is_admin:bool = Depends(check_if_admin_user)) -> typing.Dict[str, str]:


    """

    Replace the database with a backup

    Args:
    file (UploadFile): The backup file
    db (Session): The database session
    current_user (str): The current user

    Returns:
    typing.Dict[str, str]: The result of the operation

    """

    await check_internal_request(request)

    if(not is_admin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this action.")

    try:
        global maintenance_mode
        with maintenance_lock:
            maintenance_mode = True

            async with aiofiles.open("backup.zip.pgp", "wb") as buffer:
                await buffer.write(await file.read())

            async with aiofiles.open("backup.zip.pgp", "rb") as f:
                decrypted_file = await decrypt_file("backup.zip.pgp", ENCRYPTION_KEY) # type: ignore

            async with aiofiles.open(decrypted_file, "rb") as f:
                decompressed_file = await decompress_file(decrypted_file, "backup.db")

            db_path = os.path.join(os.path.dirname(__file__), "..", "database", "kakusui.db")

            await replace_sqlite_db(engine, decompressed_file, db_path)

            await asyncio.to_thread(os.remove, "backup.zip.pgp")
            await asyncio.to_thread(os.remove, decrypted_file)

        return {"message": "Database replaced successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        with maintenance_lock:
            maintenance_mode = False

@router.post("/admin/db/run-query")
async def run_query(
    request:Request,
    sql_query:str = Body(..., embed=True),
    is_admin:bool = Depends(check_if_admin_user),
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    Execute an SQL query on the database and return the result as JSON

    Args:
    request (Request): The incoming request
    sql_query (str): The SQL query to execute
    is_admin (bool): Flag to check if the user is an admin
    db (Session): The database session

    Returns:
    JSONResponse: The result of the query in JSON format or an error message
    """

    await check_internal_request(request)

    if(not is_admin):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to perform this action.")

    try:

        if(sql_query.lower() in ["force absolute reset"]):

            db.execute(text("DROP TABLE IF EXISTS users;"))

            db.execute(text("DROP TABLE IF EXISTS email_alerts;"))

            result = {"result": "Database reset successfully"}

        else:
            
            if(sql_query.lower() in ["tables", "show tables"]):
                sql_query = "SELECT name FROM sqlite_master WHERE type='table';"

            result = db.execute(text(sql_query))
            db.commit()
            
            if(result.returns_rows): # type: ignore
                columns = result.keys()
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                result = {"result": rows}
            else:
                affected_rows = result.rowcount # type: ignore
                result = {"result": f"Query executed successfully. Affected rows: {affected_rows}"}

        return JSONResponse(content=result)

    except ValueError as ve:
        return JSONResponse(
            status_code=400,
            content={"error": str(ve)}
        )
    except SQLAlchemyError as sqle:
        return JSONResponse(
            status_code=400,
            content={"error": f"SQL Error: {str(sqle)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected error: {str(e)}"}
        )

@router.get("/user/info")
async def get_user_info(
    request: Request,
    fields: typing.Optional[typing.List[str]] = None,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about the current logged-in user.
    
    Args:
    request (Request): The incoming request
    fields (Optional[List[str]]): List of fields to return. If None, returns all fields.
    current_user (str): The email of the current logged-in user
    db (Session): The database session

    Returns:
    dict: The user information
    """
    
    await check_internal_request(request)

    if(not current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        query = select(User)
        if(fields):
            query = select(*[getattr(User, field) for field in fields if hasattr(User, field)])
        
        user = db.execute(query.filter(User.email == current_user)).first()

        if(not user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if(fields):
            return {field: getattr(user[0], field) for field in fields if hasattr(User, field)}
        else:
            return {column.name: getattr(user[0], column.name) for column in User.__table__.columns}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

    finally:
        db.close()