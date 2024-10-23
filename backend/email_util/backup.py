## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import asyncio
import shutil
import zipfile
import logging

from datetime import datetime

from sqlalchemy.engine import Engine
from sqlalchemy.orm import close_all_sessions, Session

from gnupg import GPG

## custom imports
from constants import DATABASE_PATH, ENVIRONMENT

from db.models import EmailAlertModel, User

from email_util.common import get_smtp_envs, send_email


async def export_db(db_path:str, export_path:str) -> str:

    """

    Export the SQLite database to a new file

    Args:
    db_path (str): The path to the SQLite database file
    export_path (str): The path to the exported SQLite database file

    Returns:
    export_path (str): The path to the exported SQLite database file

    """

    await asyncio.to_thread(shutil.copy, db_path, export_path)
    return export_path

##----------------------------------/----------------------------------##

async def encrypt_file(file_path:str, passphrase:str) -> str:

    """

    Encrypt the file using the GPG encryption algorithm

    Args:
    file_path (str): The path to the file to encrypt
    passphrase (str): The passphrase to encrypt the file with

    Returns:
    encrypted_path (str): The path to the encrypted file

    """

    gpg = GPG()
    encrypted_path = file_path + '.pgp'
    
    with open(file_path, 'rb') as f:
        status = await asyncio.to_thread(gpg.encrypt_file, f, recipients=None, symmetric=True, passphrase=passphrase, output=encrypted_path)
        
    if(not status.ok):
        raise ValueError('Failed to encrypt the file:', status.stderr)
    
    logging.info(f"Note that Error Code 2 is acceptable. This is a known issue with encrypting with an unsigned key/passphrase.")

    return encrypted_path

##----------------------------------/----------------------------------##

async def decrypt_file(file_path:str, passphrase:str) -> str:

    """

    Decrypt the file using the GPG encryption algorithm

    Args:
    file_path (str): The path to the file to decrypt

    Returns:
    decrypted_path (str): The path to the decrypted file

    """

    gpg = GPG()
    decrypted_path = file_path.replace('.pgp', '')
    
    with open(file_path, 'rb') as f:
        status = await asyncio.to_thread(gpg.decrypt_file, f, passphrase=passphrase, output=decrypted_path)
        
    if(not status.ok):
        raise ValueError('Failed to decrypt the file:', status.stderr)
    
    logging.info(f"Note that Error Code 2 is acceptable. This is a known issue with decrypting with an unsigned key/passphrase.")

    return decrypted_path

##----------------------------------/----------------------------------##

async def compress_file(file_path:str) -> str:

    """

    Compress the file into a zip archive

    Args:
    file_path (str): The path to the file to compress

    Returns:
    compressed_path (str): The path to the compressed file

    """

    compressed_path = file_path + '.zip'

    with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        await asyncio.to_thread(zipf.write, file_path, os.path.basename(file_path))

    return compressed_path

async def decompress_file(file_path:str, decompressed_path:str) -> str:

    """

    Decompress the file from a zip archive

    Args:
    file_path (str): The path to the file to decompress

    Returns:
    decompressed_path (str): The path to the decompressed file

    """
    
    with zipfile.ZipFile(file_path, 'r') as zipf:
        
        ## Extract all files to a temporary directory
        temp_dir = os.path.join(os.getcwd(), "temp_extracted")
        await asyncio.to_thread(os.makedirs, temp_dir, exist_ok=True)
        await asyncio.to_thread(zipf.extractall, temp_dir)
        
        extracted_files = os.listdir(temp_dir)
        
        if(not extracted_files):
            raise FileNotFoundError("No files found in the zip archive")
        
        extracted_file = extracted_files[0]
        extracted_file_path = os.path.join(temp_dir, extracted_file)
        
        await asyncio.to_thread(shutil.move, extracted_file_path, decompressed_path)
    
        await asyncio.to_thread(shutil.rmtree, temp_dir)
        
    return decompressed_path

async def perform_backup(db:Session) -> None:

    """

    Perform the backup process

    """

    logging.info("Starting database backup process")

    ENCRYPTION_KEY, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, TO_EMAIL = await get_smtp_envs()

    timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")

    number_of_email_alerts = db.query(EmailAlertModel).count()
    number_of_users = db.query(User).count()

    logging.info(f"Database stats: {number_of_email_alerts} email alerts, {number_of_users} users")

    export_path = f'exported_db_{timestamp}.db'
    
    logging.info(f"Exporting database to {export_path}")
    await export_db(DATABASE_PATH, export_path)

    logging.info("Compressing exported database")
    compressed_path = await compress_file(export_path)
    await asyncio.to_thread(os.remove, export_path)

    logging.info("Encrypting compressed database")
    encrypted_path = await encrypt_file(compressed_path, ENCRYPTION_KEY)
    await asyncio.to_thread(os.remove, compressed_path)

    if(ENVIRONMENT == 'production'):

        logging.info("Sending backup email")
        await send_email(
            subject=f'SQLite Database Backup ({timestamp})',
            body=(
                'Please find the attached encrypted and compressed SQLite database backup. '
                'This email was sent automatically. Do not reply.\n\n'
                f'Number of email alerts in the database: {number_of_email_alerts}\n'
                f'Number of users in the database: {number_of_users}'
            ),
            to_email=TO_EMAIL,
            attachment_path=encrypted_path,
            from_email=FROM_EMAIL,
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            smtp_user=SMTP_USER,
            smtp_password=SMTP_PASSWORD
        )

    else:
        logging.info("Email was prepped for production, but environment is not production. Email not sent.")

    logging.info("Cleaning up temporary files")
    await asyncio.to_thread(os.remove, encrypted_path)

    try:
        await asyncio.to_thread(os.remove, export_path)
        await asyncio.to_thread(os.remove, compressed_path)
        await asyncio.to_thread(os.remove, encrypted_path)
    except Exception as e:
        pass

    finally:
        try:
            await asyncio.to_thread(os.remove, export_path)
            await asyncio.to_thread(os.remove, compressed_path)
            await asyncio.to_thread(os.remove, encrypted_path)
        except Exception as e:
            pass

    logging.info("Database backup process completed successfully")

##----------------------------------/----------------------------------##

async def perform_backup_scheduled(db: Session) -> None:
    """
    Perform the backup process on a scheduled interval
    """
    await perform_backup(db)

async def replace_sqlite_db(engine:Engine, extracted_db_path: str, current_db_path: str) -> None:
    """
    Replace the current SQLite database with the extracted SQLite database and restart the application.

    Args:
    engine (Engine): The SQLAlchemy engine
    extracted_db_path (str): The path to the extracted SQLite database
    current_db_path (str): The path to the current SQLite database
    """
    
    close_all_sessions()
    
    await asyncio.to_thread(engine.dispose)
    
    await asyncio.to_thread(os.replace, extracted_db_path, current_db_path)
