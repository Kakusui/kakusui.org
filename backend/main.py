## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## built-in libraries
import json
import os
import threading
import typing
import time
import shutil
import zipfile
import smtplib

from datetime import datetime, timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

## third-party libraries
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from kairyou import Kairyou
from kairyou.exceptions import InvalidReplacementJsonKeys, InvalidReplacementJsonName, SpacyModelNotFound

from easytl import EasyTL

from elucidate import Elucidate, __version__ as ELUCIDATE_VERSION

import httpx

from gnupg import GPG

import atexit
import shelve

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, HTTPBasic

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta, Session


from apscheduler.schedulers.background import BackgroundScheduler

##-----------------------------------------start-of-utility-functions----------------------------------------------------------------------------------------------------------------------------------------------------------

def get_url() -> str:
    if(ENVIRONMENT == "development"):
        return "http://api.localhost:5000"
    
    return "https://api.kakusui.org"

def get_env_variables() -> None:

    """

    Only used in development. This function reads the .env file and sets the environment variables.

    """

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

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

TOKEN_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 1440

if(not os.path.exists("database") and ADMIN_USER == "admin"):
    os.makedirs("database", exist_ok=True)

elif(not os.path.exists("database") and ADMIN_USER != "admin"):
    raise NotImplementedError("Database volume not attached and running in production mode, please exit and attach the volume")

TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

V1_KAIRYOU_ROOT_KEY = os.environ.get("V1_KAIRYOU_ROOT_KEY")
V1_EASYTL_ROOT_KEY = os.environ.get("V1_EASYTL_ROOT_KEY")
V1_ELUCIDATE_ROOT_KEY = os.environ.get("V1_ELUCIDATE_ROOT_KEY")

DATABASE_URL: str = "sqlite:///./database/blog.db"
DATABASE_PATH: str = "database/blog.db"
BACKUP_LOGS_DIR = 'database/logs'

Base:DeclarativeMeta = declarative_base()

security = HTTPBasic()

if(not os.path.exists(BACKUP_LOGS_DIR)):
    os.makedirs(BACKUP_LOGS_DIR, exist_ok=True)

if(not any([ADMIN_USER, ADMIN_PASS_HASH, TOTP_SECRET, ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET, ENCRYPTION_KEY, V1_KAIRYOU_ROOT_KEY, V1_EASYTL_ROOT_KEY, V1_ELUCIDATE_ROOT_KEY])):
    get_env_variables()
    ADMIN_USER = os.environ.get("ADMIN_USER")
    ADMIN_PASS_HASH = os.environ.get("ADMIN_PASS_HASH")
    TOTP_SECRET = os.environ.get("TOTP_SECRET")
    ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
    REFRESH_TOKEN_SECRET = os.environ.get("REFRESH_TOKEN_SECRET")
    ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
    V1_KAIRYOU_ROOT_KEY = os.environ.get("V1_KAIRYOU_ROOT_KEY")
    V1_EASYTL_ROOT_KEY = os.environ.get("V1_EASYTL_ROOT_KEY")
    V1_ELUCIDATE_ROOT_KEY = os.environ.get("V1_ELUCIDATE_ROOT_KEY")

assert ADMIN_USER, "ADMIN_USER environment variable not set"
assert ADMIN_PASS_HASH, "ADMIN_PASS_HASH environment variable not set"
assert TOTP_SECRET, "TOTP_SECRET environment variable not set"
assert ACCESS_TOKEN_SECRET, "ACCESS_TOKEN_SECRET environment variable not set"
assert REFRESH_TOKEN_SECRET, "REFRESH_TOKEN_SECRET environment variable not set"
assert ENCRYPTION_KEY, "ENCRYPTION_KEY environment variable not set"
assert V1_KAIRYOU_ROOT_KEY, "V1_KAIRYOU_ROOT_KEY environment variable not set"
assert V1_EASYTL_ROOT_KEY, "V1_EASYTL_ROOT_KEY environment variable not set"
assert V1_ELUCIDATE_ROOT_KEY, "V1_ELUCIDATE_ROOT_KEY environment variable not set"

##-----------------------------------------start-of-pydantic-models----------------------------------------------------------------------------------------------------------------------------------------------------------

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

##----------------------------------/----------------------------------##

def get_envs() -> typing.Tuple[str, str, int, str, str, str, str]:

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

def send_email(subject:str, body:str, to_email:str, attachment_path:str, from_email:str, smtp_server:str, smtp_port:int, smtp_user:str, smtp_password:str) -> None:

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

    ENCRYPTION_KEY, SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, TO_EMAIL = get_envs()

    timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")

    ## engine:Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    ## SessionLocal:sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    ## db:Session = SessionLocal()

    export_path = f'exported_db_{timestamp}.db'

    export_db(DATABASE_PATH, export_path)

    compressed_path = compress_file(export_path)
    os.remove(export_path)

    encrypted_path = encrypt_file(compressed_path, ENCRYPTION_KEY)
    os.remove(compressed_path)

    send_email(
        subject=f'SQLite Database Backup ({timestamp})',
        body='Please find the attached encrypted and compressed SQLite database backup. This email was sent automatically. Do not reply.',
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
        perform_backup_scheduled()

    scheduler = BackgroundScheduler()
    scheduler.add_job(perform_backup_scheduled, 'interval', hours=6)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())


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

    if(api_key != V1_EASYTL_ROOT_KEY):
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
    
##-----------------------------------------start-of-util_endpoints----------------------------------------------------------------------------------------------------------------------------------------------------------

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