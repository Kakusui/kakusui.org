## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

import typing
import os
import shutil

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request

from sqlalchemy.orm import Session

from email_util.backup import perform_backup, decrypt_file, decompress_file, replace_sqlite_db

from db.common import get_db
from db.base import engine

from auth.func import check_if_admin_user
from auth.util import check_internal_request

from constants import ENCRYPTION_KEY

from main import maintenance_mode, maintenance_lock

router = APIRouter()

@router.post('/force-backup')
def force_backup(request:Request, is_admin:bool = Depends(check_if_admin_user), db:Session = Depends(get_db)) -> typing.Dict[str, str]:

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

@router.post("/replace-database")
async def upload_backup(request:Request, file: UploadFile = File(...), db:Session = Depends(get_db), is_admin:bool = Depends(check_if_admin_user)) -> typing.Dict[str, str]:

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

            replace_sqlite_db(engine, decompressed_file, "blog.db")

            os.remove("backup.zip.pgp")
            os.remove(decrypted_file)

        return {"message": "Database replaced successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        with maintenance_lock:
            maintenance_mode = False