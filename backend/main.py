## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## built-in libraries
from uuid import uuid4

import atexit
import json
import os
import random
import shelve
import shutil
import smtplib
import string
import threading
import time
import typing
import zipfile

from datetime import datetime, timedelta, timezone
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

## third-party libraries
import httpx
import jwt

from apscheduler.schedulers.background import BackgroundScheduler
from easytl import EasyTL
from elucidate import Elucidate, __version__ as ELUCIDATE_VERSION
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
from gnupg import GPG
from jwt import PyJWTError
from kairyou import Kairyou
from kairyou.exceptions import (InvalidReplacementJsonKeys, InvalidReplacementJsonName, SpacyModelNotFound)
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.dialects.postgresql import UUID as modelUUID
from sqlalchemy.engine import Engine, Inspector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeMeta, Session, close_all_sessions, sessionmaker
from werkzeug.utils import secure_filename

##-----------------------------------------start-of-security----------------------------------------------------------------------------------------------------------------------------------------------------------

def get_secure_path(base_dir: str, filename: str) -> str:
    secure_name = secure_filename(filename)
    return os.path.join(base_dir, secure_name)

##-----------------------------------------start-of-pydantic-models----------------------------------------------------------------------------------------------------------------------------------------------------------

class LoginModel(BaseModel):
    email:str
    verification_code:str

class LoginToken(BaseModel):
    access_token:str
    token_type:str
    refresh_token:str

class TokenData(BaseModel):
    email:str

class SendVerificationEmailRequest(BaseModel):
    email:str
    clientID:str

class VerifyEmailCodeRequest(BaseModel):
    email:str
    code:str

class RegisterForEmailAlert(BaseModel):
    email:str

class KairyouRequest(BaseModel):
    textToPreprocess:str
    replacementsJson:str

class EasyTLRequest(BaseModel):
    textToTranslate:str
    translationInstructions:str
    llmType:str
    userAPIKey:str
    model:str

class ElucidateRequest(BaseModel):
    textToEvaluate:str
    evaluationInstructions:str
    llmType:str
    userAPIKey:str
    model:str

class VerifyTurnstileRequest(BaseModel):
    token:str

##-----------------------------------------start-of-utility-functions----------------------------------------------------------------------------------------------------------------------------------------------------------

def get_url() -> str:
    if(ENVIRONMENT == "development"):
        return "http://api.localhost:5000"
    
    return "https://api.kakusui.org"

def get_env_variables() -> None:

    """

    Only used in development. This function reads the .env file and sets the environment variables.

    """

    if(not os.path.exists(".env")):
        return

    with open(".env") as f:
        for line in f:
            key, value = line.strip().split("=")
            os.environ[key] = value

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------
get_env_variables()

maintenance_mode = False
maintenance_lock = threading.Lock()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_PASS_HASH = os.environ.get("ADMIN_PASS_HASH")
TOTP_SECRET = os.environ.get("TOTP_SECRET")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
REFRESH_TOKEN_SECRET = os.environ.get("REFRESH_TOKEN_SECRET")
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

TOKEN_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 43200 ## 30 days
VERIFICATION_EXPIRATION_MINUTES = 5
MAX_REQUESTS = 5
MAX_REQUESTS_PER_ID = 10
MAX_REQUESTS_PER_EMAIL = 5
RATE_LIMIT_WINDOW = 3600

if(not os.path.exists("database") and ACCESS_TOKEN_SECRET == "secret"):
    os.makedirs("database", exist_ok=True)

elif(not os.path.exists("database") and ACCESS_TOKEN_SECRET != "secret"):
    raise NotImplementedError("Database volume not attached and running in production mode, please exit and attach the volume")

V1_KAIRYOU_ROOT_KEY = os.environ.get("V1_KAIRYOU_ROOT_KEY")
V1_EASYTL_ROOT_KEY = os.environ.get("V1_EASYTL_ROOT_KEY")
V1_EASYTL_PUBLIC_API_KEY = os.environ.get("V1_EASYTL_PUBLIC_API_KEY")
V1_ELUCIDATE_ROOT_KEY = os.environ.get("V1_ELUCIDATE_ROOT_KEY")

DATABASE_URL: str = "sqlite:///./database/kakusui.db"
DATABASE_PATH: str = "database/kakusui.db"
BACKUP_LOGS_DIR = 'database/logs'
VERIFICATION_DATA_DIR = 'database/temp_verification'
RATE_LIMIT_DATA_DIR = 'database/rate_limit'

Base:DeclarativeMeta = declarative_base()

security = HTTPBasic()

if(not os.path.exists(BACKUP_LOGS_DIR)):
    os.makedirs(BACKUP_LOGS_DIR, exist_ok=True)

envs = [TURNSTILE_SECRET_KEY, 
        ENCRYPTION_KEY, 
        ADMIN_USER, 
        ADMIN_PASS_HASH, 
        TOTP_SECRET, 
        ACCESS_TOKEN_SECRET, 
        REFRESH_TOKEN_SECRET, 
        V1_KAIRYOU_ROOT_KEY, 
        V1_EASYTL_ROOT_KEY, 
        V1_EASYTL_PUBLIC_API_KEY, 
        V1_ELUCIDATE_ROOT_KEY]

for env in envs:
    assert env, f"{env} environment variable not set"

##----------------------------------/----------------------------------##

class EmailAlertModel(Base):
    __tablename__ = "email_alerts"
    id = Column(modelUUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    email = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

##----------------------------------/----------------------------------##

engine:Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal:sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables_if_not_exist(engine, base:DeclarativeMeta) -> None:
    inspector:Inspector = inspect(engine)
    for table_name in base.metadata.tables.keys():
        if(not inspector.has_table(table_name)):
            base.metadata.tables[table_name].create(engine)

create_tables_if_not_exist(engine, Base)

##----------------------------------/----------------------------------##

def get_smtp_envs() -> typing.Tuple[str, str, int, str, str, str, str]:

    """
    
    Get the environment variables from the .env file

    Returns:
    ENCRYPTION_KEY (str): The encryption key to encrypt/decrypt the database
    SMTP_SERVER (str): The SMTP server to send the email
    SMTP_PORT (int): The SMTP port to send the email
    SMTP_USER (str): The SMTP user to send the email
    SMTP_PASSWORD (str): The SMTP password to send the email
    FROM_EMAIL (str): The email address to send the email from
    TO_EMAIL (str): The email address to send the email to

    """

    if(os.path.exists(".env")):
        with open(".env", "r") as f:
            for line in f:
                key, value = line.strip().split("=")
                os.environ[key] = value

    ENCRYPTION_KEY:str = os.getenv('ENCRYPTION_KEY') or ""
    SMTP_SERVER:str = os.getenv('SMTP_SERVER') or ""
    SMTP_PORT:int = int(os.getenv('SMTP_PORT') or 0)
    SMTP_USER = os.getenv('SMTP_USER') or ""
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD') or ""
    FROM_EMAIL = os.getenv('FROM_EMAIL') or ""
    TO_EMAIL = os.getenv('TO_EMAIL') or ""

    assert(ENCRYPTION_KEY != ""), "ENCRYPTION_KEY is required"
    assert(SMTP_SERVER != ""), "SMTP_SERVER is required"
    assert(SMTP_PORT != 0), "SMTP_PORT is required"
    assert(SMTP_USER != ""), "SMTP_USER is required"
    assert(SMTP_PASSWORD != ""), "SMTP_PASSWORD is required"
    assert(FROM_EMAIL != ""), "FROM_EMAIL is required"
    assert(TO_EMAIL != ""), "TO_EMAIL is required"

    return ENCRYPTION_KEY, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, TO_EMAIL

##-----------------------------------------start-of-backup----------------------------------------------------------------------------------------------------------------------------------------------------------

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

##----------------------------------/----------------------------------##

def send_email(subject:str, body:str, to_email:str, attachment_path:str | None, from_email:str, smtp_server:str, smtp_port:int, smtp_user:str, smtp_password:str) -> None:

    """

    Send an email with an attachment

    Args:
    subject (str): The subject of the email
    body (str): The body of the email
    to_email (str): The email address to send the email to
    attachment_path (str): The path to the attachment to send
    from_email (str): The email address to send the email from
    smtp_server (str): The SMTP server to send the email
    smtp_port (int): The SMTP port to send the email
    smtp_user (str): The SMTP user to send the email
    smtp_password (str): The SMTP password to send the email

    """


    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    msg.attach(MIMEText(body, 'plain'))

    if(attachment_path is not None):

        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
            msg.attach(part)

    try:

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() 
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()

    except Exception as e:
        print(f"Error: {e}")

##----------------------------------/----------------------------------##

def perform_backup() -> None:

    """

    Perform the backup process

    """

    ENCRYPTION_KEY, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, TO_EMAIL = get_smtp_envs()

    timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")

    db:Session = SessionLocal()

    number_of_email_alerts = db.query(EmailAlertModel).count()

    export_path = f'exported_db_{timestamp}.db'

    export_db(DATABASE_PATH, export_path)

    compressed_path = compress_file(export_path)
    os.remove(export_path)

    encrypted_path = encrypt_file(compressed_path, ENCRYPTION_KEY)
    os.remove(compressed_path)

    send_email(
        subject=f'SQLite Database Backup ({timestamp})',
        body='Please find the attached encrypted and compressed SQLite database backup. This email was sent automatically. Do not reply.\n\nNumber of email alerts in the database: ' + str(number_of_email_alerts),
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

def perform_backup_scheduled() -> None:

    """

    Perform the backup process on a scheduled interval

    """

    with shelve.open(os.path.join(BACKUP_LOGS_DIR, 'backup_scheduler.db')) as db:
        perform_backup()
        db['last_run'] = datetime.now()

##----------------------------------/----------------------------------##

def start_scheduler():
    max_retries = 5
    retry_delay = 3

    for _ in range(max_retries):
        try:
            with shelve.open(os.path.join(BACKUP_LOGS_DIR, 'backup_scheduler.db')) as db:
                last_run = db.get('last_run', None)

                should_run_initial = True
                if(last_run):
                    time_since_last_run = datetime.now() - last_run
                    if(time_since_last_run < timedelta(hours=6)):
                        should_run_initial = False

            break

        except Exception as e:
            if("Resource temporarily unavailable" in str(e)):
                time.sleep(retry_delay)
            else:
                raise
    else:
        print("Failed to initialize scheduler after multiple attempts")
        return

    if(should_run_initial):
        cleanup_expired_codes()
        perform_backup_scheduled()

    scheduler = BackgroundScheduler()

    scheduler.add_job(perform_backup_scheduled, 'interval', hours=6)
    scheduler.add_job(cleanup_expired_codes, 'interval', hours=1)

    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())

def cleanup_expired_codes() -> None:

    if(not os.path.exists(VERIFICATION_DATA_DIR)):
        return

    current_time = datetime.now()

    for filename in os.listdir(VERIFICATION_DATA_DIR):
        file_path = os.path.join(VERIFICATION_DATA_DIR, filename)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            expiration_time = datetime.fromisoformat(data['expiration'])

            if(current_time > expiration_time):
                os.remove(file_path)
                print(f"Removed expired verification code for {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

    if(not os.path.exists(RATE_LIMIT_DATA_DIR)):
        return

    for filename in os.listdir(RATE_LIMIT_DATA_DIR):
        file_path = os.path.join(RATE_LIMIT_DATA_DIR, filename)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            blocked_until = data.get('blocked_until')

            if(blocked_until and current_time.timestamp() > blocked_until):
                os.remove(file_path)
                print(f"Removed expired rate limit file for {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

##----------------------------------/----------------------------------##

def rate_limit(email:str, id:str) -> None:

    if(not os.path.exists(RATE_LIMIT_DATA_DIR)):
        os.makedirs(RATE_LIMIT_DATA_DIR)

    email_data = load_rate_limit_data(email, is_email=True)
    check_and_update_rate_limit(email_data, MAX_REQUESTS_PER_EMAIL, "email")

    id_data = load_rate_limit_data(id, is_email=False)
    check_and_update_rate_limit(id_data, MAX_REQUESTS_PER_ID, "ID")

    save_rate_limit_data(email, is_email=True, data=email_data)
    save_rate_limit_data(id, is_email=False, data=id_data)

def load_rate_limit_data(email_or_id:str, is_email:bool) -> dict:
    directory = RATE_LIMIT_DATA_DIR
    prefix = "email_" if is_email else "id_"
    filename = f"{prefix}{email_or_id}.json"
    file_path = get_secure_path(directory, filename)

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
        
    except FileNotFoundError:
        return {"requests": [], "blocked_until": None}

def save_rate_limit_data(email_or_id:str, is_email:bool, data:dict) -> None:

    directory = RATE_LIMIT_DATA_DIR
    prefix = "email_" if is_email else "id_"
    filename = f"{prefix}{email_or_id}.json"
    file_path = get_secure_path(directory, filename)

    with open(file_path, 'w') as f:
        json.dump(data, f)

def check_and_update_rate_limit(data:dict, max_requests:int, limit_type:str) -> None:
    current_time = time.time()

    data['requests'] = [req for req in data['requests'] if current_time - req < RATE_LIMIT_WINDOW]

    if(data['blocked_until'] and current_time < data['blocked_until']):
        raise HTTPException(status_code=429, detail=f"Too many requests from this {limit_type}. Please try again later.")

    if(len(data['requests']) >= max_requests):
        data['blocked_until'] = current_time + RATE_LIMIT_WINDOW
        raise HTTPException(status_code=429, detail=f"Too many requests from this {limit_type}. Please try again later.")

    data['requests'].append(current_time)

##-----------------------------------------start-of-auth----------------------------------------------------------------------------------------------------------------------------------------------------------

def create_access_token(data:dict, expires_delta:typing.Optional[timedelta] = None) -> str:

    """
    
    Create an access token with the given data and expiration time

    Args:
    data (dict): The data to encode into the token
    expires_delta (timedelta): The time until the token expires

    Returns:
    encoded_jwt (str): The encoded JWT token

    """

    to_encode = data.copy()

    if(expires_delta):
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET, algorithm=TOKEN_ALGORITHM) # type: ignore
    return encoded_jwt

def create_refresh_token(data:dict, expires_delta:typing.Optional[timedelta] = None) -> str:

    """

    Create a refresh token with the given data and expiration time

    Args:
    data (dict): The data to encode into the token
    expires_delta (timedelta): The time until the token expires

    Returns:
    encoded_jwt (str): The encoded JWT token

    """

    to_encode = data.copy()

    if(expires_delta):
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=1)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm=TOKEN_ALGORITHM) # type: ignore
    return encoded_jwt

def verify_verification_code(email: str, verification_code: str) -> bool:

    """

    Verify the given verification code for the given email

    Args:
    email (str): The email to verify
    verification_code (str): The verification code to verify

    Returns:

    bool: True if the verification code is valid, False otherwise

    """

    verification_data = get_verification_data(email)
    if(not verification_data):
        return False
    
    stored_code = verification_data["code"]
    expiration_time = datetime.fromisoformat(verification_data["expiration"])
    
    if(datetime.now() > expiration_time):
        return False
    
    remove_verification_data(email)
    
    return verification_code == stored_code

def func_verify_token(token:str) -> TokenData:

    """

    Verify the given token and return the data

    Args:    
    token (str): The token to verify

    Returns:
    TokenData: The data from the token

    """

    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=[TOKEN_ALGORITHM]) # type: ignore
        email:str = payload.get("sub")

        if(email is None):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return TokenData(email=email)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
def get_current_user(token:str = Depends(oauth2_scheme)):

    """

    Get the current user from the given token

    Args:
    token (str): The token to get the user from

    Returns:
    str: The email of the user

    """

    try:
        token_data = func_verify_token(token)
        return token_data.email
    except HTTPException as e:
        raise e

def get_current_active_user(current_user:str = Depends(get_current_user)):

    """

    Get the current active user

    Args:
    current_user (str): The current user

    Returns:
    str: The username of the user

    """

    if(current_user != ADMIN_USER):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return current_user

##-----------------------------------------start-of-database----------------------------------------------------------------------------------------------------------------------------------------------------------

def replace_sqlite_db(extracted_db_path:str, current_db_path:str) -> None:

    """

    Replace the current SQLite database with the extracted SQLite database.

    Args:
    extracted_db_path (str): The path to the extracted SQLite database

    current_db_path (str): The path to the current SQLite database
    
    """

    global engine, SessionLocal

    close_all_sessions()
    
    engine.dispose()
    
    os.replace(extracted_db_path, current_db_path)

    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> typing.Generator[Session, None, None]:
    
    """

    Get the database session.

    Returns:
    typing.Generator[Session, None, None]: The database session

    """

    db:Session = SessionLocal()
    
    try:
        yield db
    
    finally:
        db.close()

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    start_scheduler()

##-----------------------------------------start-of-middleware----------------------------------------------------------------------------------------------------------------------------------------------------------

@app.middleware("http")
async def maintenance_middleware(request:Request, call_next):
    global maintenance_mode
    if(maintenance_mode):
        return JSONResponse(status_code=503, content={"message": "Server is in maintenance mode"})
    
    response = await call_next(request)
    
    return response

## CORS setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

##-----------------------------------------start-of-warmup_endpoints----------------------------------------------------------------------------------------------------------------------------------------------------------


@app.get("/")
async def api_home():
    return {"message": "Welcome to the API"}

@app.get("/v1/kairyou")
async def kairyou_warm_up():
    return {"message": "Kairyou is running."}

@app.get("/v1/easytl")
async def easytl_warm_up():
    return {"message": "EasyTL is running."}

@app.get("/v1/elucidate")
async def elucidate_warm_up():
    return {"message": "Elucidate is running."}

##-----------------------------------------start-of-kairyou_endpoints----------------------------------------------------------------------------------------------------------------------------------------------------------

## if and when we ever actually open this up to the public, we will need to add a rate limiter

@app.post("/v1/kairyou")
async def kairyou(request_data:KairyouRequest, request:Request):
    text_to_preprocess = request_data.textToPreprocess
    replacements_json = request_data.replacementsJson
    
    api_key = request.headers.get("X-API-Key")

    if(api_key != V1_KAIRYOU_ROOT_KEY):
        return JSONResponse(status_code=401, content={
            "message": "Invalid endpoint API key. If you are actually interested in using this endpoint, please contact us at contact@kakusui.org."
        })

    if(len(text_to_preprocess) > 175000):
        return JSONResponse(status_code=400, content={
            "message": "The text to preprocess is too long. Please keep it under 175,000 characters."
        })

    try:
        replacements_json = json.loads(replacements_json)

        preprocessed_text, preprocessing_log, error_log = Kairyou.preprocess(text_to_preprocess, replacements_json)

        return JSONResponse(status_code=200, content={
            "preprocessedText": preprocessed_text,
            "preprocessingLog": preprocessing_log,
            "errorLog": error_log
        })

    except (InvalidReplacementJsonKeys, InvalidReplacementJsonName):
        return JSONResponse(status_code=400, content={
            "message": "You have an invalid replacement json file. Please see https://github.com/Bikatr7/Kairyou?tab=readme-ov-file#kairyou for usage."
        })

    except SpacyModelNotFound:
        return JSONResponse(status_code=500, content={
            "message": "An internal error occurred. Please contact the administrator."
        })


##-----------------------------------------start-of-easytl_endpoints----------------------------------------------------------------------------------------------------------------------------------------------------------

## if and when we ever actually open this up to the public, we will need to add a rate limiter

@app.post("/v1/easytl")
async def easytl(request_data:EasyTLRequest, request:Request):
    text_to_translate = request_data.textToTranslate
    translation_instructions = request_data.translationInstructions
    llm_type = request_data.llmType.lower()
    user_api_key = request_data.userAPIKey
    model = request_data.model

    api_key = request.headers.get("X-API-Key")

    MAX_TEXT_LENGTH = 100000
    MAX_INSTRUCTIONS_LENGTH = 5000
    VALID_LLM_TYPES = ["anthropic", "openai", "gemini"]

    ERRORS = {
        "invalid_api_key": {"status_code": 401, "content": {"message": "Invalid endpoint API key. If you are actually interested in using this endpoint, please contact us at contact@kakusui.org."}},
        "text_too_long": {"status_code": 400, "content": {"message": "The text to translate is too long. Please keep it under 10,000 characters."}},
        "instructions_too_long": {"status_code": 400, "content": {"message": "The translation instructions are too long. Please keep it under 1,000 characters."}},
        "invalid_llm_type": {"status_code": 400, "content": {"message": "Invalid LLM type. Please use 'anthropic', 'openai', or 'gemini'."}},
        "invalid_user_api_key": {"status_code": 401, "content": {"message": "Invalid user API key. Please check your credentials."}},
        "internal_error": {"status_code": 500, "content": {"message": "An internal error occurred. Please try again later."}}
    }

    ## these models don't listen to translation instructions well, so we need to do something different
    ## what we do is put the instructions in the text to translate
    unsophisticated_models_whitelist = [
        "gpt-3.5-turbo",
        "claude-3-haiku-20240307", 
        "claude-3-sonnet-20240229", 
        "claude-3-opus-20240229"
    ]

    if(api_key not in [V1_EASYTL_ROOT_KEY, V1_EASYTL_PUBLIC_API_KEY]):
        return JSONResponse(**ERRORS["invalid_api_key"])
    
    if(len(text_to_translate) > MAX_TEXT_LENGTH):
        return JSONResponse(**ERRORS["text_too_long"])
    
    if(len(translation_instructions) > MAX_INSTRUCTIONS_LENGTH):
        return JSONResponse(**ERRORS["instructions_too_long"])
        
    if(llm_type not in VALID_LLM_TYPES):
        return JSONResponse(**ERRORS["invalid_llm_type"])
    
    try:
        EasyTL.set_credentials(api_type=llm_type, credentials=user_api_key) # type: ignore
        EasyTL.test_credentials(api_type=llm_type) # type: ignore

    except:
        return JSONResponse(**ERRORS["invalid_user_api_key"])

    try:

        if(model in unsophisticated_models_whitelist):
            text_to_translate = f"{translation_instructions}\n{text_to_translate}"
            translation_instructions = "Your instructions are in the other text."

        translated_text = await EasyTL.translate_async(text=text_to_translate, 
                                                       service=llm_type, # type: ignore 
                                                       translation_instructions=translation_instructions,
                                                       model=model
                                                       ) 

    except:
        return JSONResponse(**ERRORS["internal_error"])

    return JSONResponse(status_code=200, content={
        "translatedText": translated_text
    })

##-----------------------------------------start-of-elucidate_endpoints----------------------------------------------------------------------------------------------------------------------------------------------------------

## if and when we ever actually open this up to the public, we will need to add a rate limiter

@app.post("/v1/elucidate")
async def elucidate(request_data:ElucidateRequest, request:Request):
    text_to_evaluate = request_data.textToEvaluate
    evaluation_instructions = request_data.evaluationInstructions
    llm_type = request_data.llmType.lower()
    user_api_key = request_data.userAPIKey
    model = request_data.model

    api_key = request.headers.get("X-API-Key")

    MAX_TEXT_LENGTH = 100000
    MAX_INSTRUCTIONS_LENGTH = 5000
    VALID_LLM_TYPES = ["openai", "anthropic", "gemini"]

    ERRORS = {
        "invalid_api_key": {"status_code": 401, "content": {"message": "Invalid endpoint API key. If you are actually interested in using this endpoint, please contact us at contact@kakusui.org."}},
        "text_too_long": {"status_code": 400, "content": {"message": "The text to evaluate is too long. Please keep it under 10,000 characters."}},
        "instructions_too_long": {"status_code": 400, "content": {"message": "The evaluation instructions are too long. Please keep it under 1,000 characters."}},
        "invalid_llm_type": {"status_code": 400, "content": {"message": f"Invalid LLM type. As of Elucidate {ELUCIDATE_VERSION}, only 'openai', 'anthropic', and 'gemini' are supported."}},
        "invalid_user_api_key": {"status_code": 401, "content": {"message": "Invalid user API key. Please check your credentials."}},
        "internal_error": {"status_code": 500, "content": {"message": "An internal error occurred. Please try again later."}}
    }

    ## these models don't listen to translation instructions well, so we need to do something different
    ## what we do is put the instructions in the text to translate
    unsophisticated_models_whitelist = [
        "gpt-3.5-turbo",
        "claude-3-haiku-20240307", 
        "claude-3-sonnet-20240229", 
        "claude-3-opus-20240229"
    ]

    if(api_key != V1_ELUCIDATE_ROOT_KEY):
        return JSONResponse(**ERRORS["invalid_api_key"])
    
    if(len(text_to_evaluate) > MAX_TEXT_LENGTH):
        return JSONResponse(**ERRORS["text_too_long"])
    
    if(len(evaluation_instructions) > MAX_INSTRUCTIONS_LENGTH):
        return JSONResponse(**ERRORS["instructions_too_long"])
        
    if(llm_type not in VALID_LLM_TYPES):
        return JSONResponse(**ERRORS["invalid_llm_type"])
    
    try:
        EasyTL.set_credentials(api_type=llm_type, credentials=user_api_key) # type: ignore
        EasyTL.test_credentials(api_type=llm_type) # type: ignore

    except:
        return JSONResponse(**ERRORS["invalid_user_api_key"])

    try:

        if(model in unsophisticated_models_whitelist):
            text_to_evaluate = f"{evaluation_instructions}\n{text_to_evaluate}"
            evaluation_instructions = "Your instructions are in the other text."

        evaluated_text = await Elucidate.evaluate_async(text=text_to_evaluate,
                                                       service=llm_type, # type: ignore 
                                                       evaluation_instructions=evaluation_instructions,
                                                       model=model
                                                       ) 

    except:
        return JSONResponse(**ERRORS["internal_error"])

    return JSONResponse(status_code=200, content={
        "evaluatedText": evaluated_text
    })

##-----------------------------------------start-of-proxy_endpoints----------------------------------------------------------------------------------------------------------------------------------------------------------
## Used only by Kakusui.org and testing environments

@app.post("/proxy/kairyou")
async def proxy_kairyou(request_data:KairyouRequest, request:Request):
    origin = request.headers.get('origin')

    allowed_domains = [
        "https://kakusui.org", 
        "http://localhost:5173",
        ".kakusui-org.pages.dev"
    ]

    if(origin is not None and not any(origin.endswith(domain) for domain in allowed_domains)):
        raise HTTPException(status_code=403, detail="Forbidden")

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_KAIRYOU_ROOT_KEY
        }
        response = await client.post(f"{get_url()}/v1/kairyou", json=request_data.model_dump(), headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())

@app.post("/proxy/easytl")
async def proxy_easytl(request_data:EasyTLRequest, request:Request):
    origin = request.headers.get('origin')

    allowed_domains = [
        "https://kakusui.org", 
        "http://localhost:5173",
        ".kakusui-org.pages.dev"
    ]

    if(origin is not None and not any(origin.endswith(domain) for domain in allowed_domains)):
        raise HTTPException(status_code=403, detail="Forbidden")

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_EASYTL_ROOT_KEY
        }
        response = await client.post(f"{get_url()}/v1/easytl", json=request_data.model_dump(), headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())
    
@app.post("/proxy/elucidate")
async def proxy_elucidate(request_data:ElucidateRequest, request:Request):
    origin = request.headers.get('origin')

    allowed_domains = [
        "https://kakusui.org", 
        "http://localhost:5173",
        ".kakusui-org.pages.dev"
    ]

    if(origin is not None and not any(origin.endswith(domain) for domain in allowed_domains)):
        raise HTTPException(status_code=403, detail="Forbidden")

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_ELUCIDATE_ROOT_KEY
        }
        response = await client.post(f"{get_url()}/v1/elucidate", json=request_data.model_dump(), headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())
    
##-----------------------------------------start-of-login_endpoints----------------------------------------------------------------------------------------------------------------------------------------------------------

@app.post("/login", response_model=LoginToken)
def login(data:LoginModel) -> typing.Dict[str, str]:
    
    """
    
    Login endpoint for the API

    Args:
    data (LoginModel): The data required to login

    Returns:
    typing.Dict[str, str]: The access token and token type

    """

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

@app.post("/refresh", response_model=LoginToken)
def refresh_token(refresh_token: str = Cookie(None)) -> JSONResponse:
    
    """

    Refresh the access token using the refresh token

    Args:
    refresh_token (str): The refresh token

    Returns:
    typing.Dict[str, str]: The access token and token type

    """

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
    
##-----------------------------------------start-of-email_auth_endpoints----------------------------------------------------------------------------------------------------------------------------------------------------------

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

    secure_email = secure_filename(email)

    with open(f"{VERIFICATION_DATA_DIR}/{secure_email}.json", "w") as f:
        json.dump(data, f)

def get_verification_data(email:str) -> dict | None:
    try:
        secure_email = secure_filename(email)
        with open(f"{VERIFICATION_DATA_DIR}/{secure_email}.json", "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return None

def remove_verification_data(email:str) -> None:
    try:
        secure_email = secure_filename(email)
        os.remove(f"{VERIFICATION_DATA_DIR}/{secure_email}.json")
    except FileNotFoundError:
        pass

def send_verification_email(email:str, code:str) -> None:
    _, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, _ = get_smtp_envs()

    subject = "Email Verification Code for Kakusui.org"
    body = f"Your verification code is {code}"

    send_email(subject=subject, body=body, to_email=email, attachment_path=None, from_email=FROM_EMAIL, smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT, smtp_user=SMTP_USER, smtp_password=SMTP_PASSWORD)

@app.post("/send-verification-email")
async def send_verification_email_endpoint(request_data: SendVerificationEmailRequest, request: Request):
    origin = request.headers.get('origin')
    allowed_domains = [
        "https://kakusui.org", 
        "http://localhost:5173",
        ".kakusui-org.pages.dev"
    ]

    if(origin is not None and not any(origin.endswith(domain) for domain in allowed_domains)):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    email = request_data.email
    client_id = request_data.clientID

    db: Session = SessionLocal()
    try:

        try:
            rate_limit(email, client_id)
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"message": e.detail})

        existing_email = db.query(EmailAlertModel).filter(EmailAlertModel.email == email).first()
        if(existing_email):
            return JSONResponse(status_code=400, content={"message": "Email already registered for alerts."})

        verification_code = generate_verification_code()
        save_verification_data(email, verification_code)
        send_verification_email(email, verification_code)

        return JSONResponse(status_code=200, content={"message": "Verification email sent successfully."})
    
    except Exception as e:
        print(f"Error sending verification email: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "An error occurred while sending the verification email."})
    
    finally:
        db.close()

@app.post("/verify-email-code")
async def verify_email_code_endpoint(request_data:VerifyEmailCodeRequest, request:Request):
    origin = request.headers.get('origin')
    allowed_domains = [
        "https://kakusui.org", 
        "http://localhost:5173",
        ".kakusui-org.pages.dev"
    ]

    if(origin is not None and not any(origin.endswith(domain) for domain in allowed_domains)):
        raise HTTPException(status_code=403, detail="Forbidden")

    email = request_data.email
    submitted_code = request_data.code

    db: Session = SessionLocal()
    try:
        verification_data = get_verification_data(email)
        if(not verification_data):
            return JSONResponse(status_code=400, content={"message": "Verification code not found or expired."})

        stored_code = verification_data["code"]
        expiration_time = datetime.fromisoformat(verification_data["expiration"])

        if(datetime.now() > expiration_time):
            remove_verification_data(email)
            return JSONResponse(status_code=400, content={"message": "Verification code has expired."})

        if(submitted_code != stored_code):
            return JSONResponse(status_code=400, content={"message": "Invalid verification code."})

        new_email_alert = EmailAlertModel(email=email)
        db.add(new_email_alert)
        db.commit()
        
        remove_verification_data(email)
        return JSONResponse(status_code=200, content={"message": "Email successfully verified and registered for alerts."})
    
    except Exception as e:
        db.rollback()
        print(f"Error verifying email code: {str(e)}")
        return JSONResponse(status_code=500, content={"message": "An error occurred while verifying the email code."})
    
    finally:
        db.close()

@app.post("/verify-token")
async def verify_token_endpoint(request: Request):
    auth_header = request.headers.get("Authorization")
    
    if(not auth_header or not auth_header.startswith("Bearer ")):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = auth_header.split(" ")[1]

    try:
        token_data = func_verify_token(token)
        return {"valid": True, "email": token_data.email}
    
    except HTTPException as e:
        return {"valid": False, "detail": str(e.detail)}

##-----------------------------------------start-of-turnstile_endpoints----------------------------------------------------------------------------------------------------------------------------------------------------------

@app.post("/verify-turnstile")
async def verify_turnstile(request_data:VerifyTurnstileRequest, request:Request):
    origin = request.headers.get('origin')
    if(origin != "https://kakusui.org"):
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        data = {
            'secret': TURNSTILE_SECRET_KEY,
            'response': request_data.token
        }

        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(url, data=data)
            result = response.json()
            
            if(result.get('success')):
                return {"success": True}
            else:
                raise HTTPException(status_code=400, detail="Turnstile verification failed")
            
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while verifying the token")