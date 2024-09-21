## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import shutil
import zipfile
import sys

from datetime import datetime

## third-party imports
import shelve

from sqlalchemy.engine import Engine
from sqlalchemy.orm import close_all_sessions, Session

from gnupg import GPG

## custom imports
from constants import DATABASE_PATH, BACKUP_LOGS_DIR

from db.models import EmailAlertModel, User

from email_util.common import get_smtp_envs, send_email


def export_db(db_path:str, export_path:str) -> str:

    """

    Export the SQLite database to a new file

    Args:
    db_path (str): The path to the SQLite database file
    export_path (str): The path to the exported SQLite database file

    Returns:
    export_path (str): The path to the exported SQLite database file

    """

    shutil.copy(db_path, export_path)
    return export_path

##----------------------------------/----------------------------------##

def encrypt_file(file_path:str, passphrase:str) -> str:

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
        status = gpg.encrypt_file(
            f, 
            recipients=None, 
            symmetric=True, 
            passphrase=passphrase, 
            output=encrypted_path
        )
        
    if(not status.ok):
        raise ValueError('Failed to encrypt the file:', status.stderr)

    return encrypted_path

##----------------------------------/----------------------------------##

def decrypt_file(file_path:str, passphrase:str) -> str:

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
        status = gpg.decrypt_file(
            f, 
            passphrase=passphrase, 
            output=decrypted_path
        )
        
    if(not status.ok):
        raise ValueError('Failed to decrypt the file:', status.stderr)

    return decrypted_path

##----------------------------------/----------------------------------##

def compress_file(file_path:str) -> str:

    """

    Compress the file into a zip archive

    Args:
    file_path (str): The path to the file to compress

    Returns:
    compressed_path (str): The path to the compressed file

    """

    compressed_path = file_path + '.zip'

    with zipfile.ZipFile(compressed_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))

    return compressed_path

def decompress_file(file_path:str, decompressed_path:str) -> str:

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
        os.makedirs(temp_dir, exist_ok=True)
        zipf.extractall(temp_dir)
        
        extracted_files = os.listdir(temp_dir)
        
        if(not extracted_files):
            raise FileNotFoundError("No files found in the zip archive")
        
        extracted_file = extracted_files[0]
        extracted_file_path = os.path.join(temp_dir, extracted_file)
        
        shutil.move(extracted_file_path, decompressed_path)
    
        shutil.rmtree(temp_dir)
        
    return decompressed_path

def perform_backup(db:Session) -> None:

    """

    Perform the backup process

    """

    ENCRYPTION_KEY, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, TO_EMAIL = get_smtp_envs()

    timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")

    number_of_email_alerts = db.query(EmailAlertModel).count()
    number_of_users = db.query(User).count()

    export_path = f'exported_db_{timestamp}.db'

    export_db(DATABASE_PATH, export_path)

    compressed_path = compress_file(export_path)
    os.remove(export_path)

    encrypted_path = encrypt_file(compressed_path, ENCRYPTION_KEY)
    os.remove(compressed_path)
    send_email(
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

    os.remove(encrypted_path)

    try:

        os.remove(export_path)
        os.remove(compressed_path)
        os.remove(encrypted_path)

    except Exception:
        pass

    finally:
        try:
            os.remove(export_path)
            os.remove(compressed_path)
            os.remove(encrypted_path)

        except:
            pass

##----------------------------------/----------------------------------##

def perform_backup_scheduled(db:Session) -> None:

    """

    Perform the backup process on a scheduled interval

    """

    with shelve.open(os.path.join(BACKUP_LOGS_DIR, 'backup_scheduler.db')) as database:
        perform_backup(db)
        database['last_run'] = datetime.now()

def replace_sqlite_db(engine:Engine, extracted_db_path: str, current_db_path: str) -> None:
    """
    Replace the current SQLite database with the extracted SQLite database and restart the application.

    Args:
    engine (Engine): The SQLAlchemy engine
    extracted_db_path (str): The path to the extracted SQLite database
    current_db_path (str): The path to the current SQLite database
    """
    
    close_all_sessions()
    
    engine.dispose()
    
    os.replace(extracted_db_path, current_db_path)

    # Restart the application
    python = sys.executable
    os.execl(python, python, *sys.argv)

