## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

import typing
import os
import shutil

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request, Body
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy import text

from email_util.backup import perform_backup, decrypt_file, decompress_file, replace_sqlite_db

from db.base import engine, get_db

from auth.func import check_if_admin_user
from auth.util import check_internal_request

from constants import ENCRYPTION_KEY

from main import maintenance_mode, maintenance_lock

router = APIRouter()

@router.post('/admin/db/force-backup')
def force_backup(request:Request, db:Session = Depends(get_db), is_admin:bool = Depends(check_if_admin_user)):

    """

    Force a backup

    Args:
    current_user (str): The current user

    Returns:
    typing.Dict[str, str]: The result of the operation

    """

    origin = request.headers.get('origin')

    check_internal_request(origin)

    perform_backup(db)

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

    origin = request.headers.get('origin')

    check_internal_request(origin)

    try:
        global maintenance_mode
        with maintenance_lock:
            maintenance_mode = True

            with open("backup.zip.pgp", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            with open("backup.zip.pgp", "rb") as f:
                decrypted_file = decrypt_file("backup.zip.pgp", ENCRYPTION_KEY) # type: ignore

            with open(decrypted_file, "rb") as f:
                decompressed_file = decompress_file(decrypted_file, "backup.db")

            db_path = os.path.join(os.path.dirname(__file__), "..", "database", "kakusui.db")

            replace_sqlite_db(engine, decompressed_file, db_path)

            os.remove("backup.zip.pgp")
            os.remove(decrypted_file)

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
    JSONResponse: The result of the query in JSON format
    """

    origin = request.headers.get('origin')
    check_internal_request(origin)

    try:
        result = db.execute(text(sql_query))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return JSONResponse(content={"result": rows})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))