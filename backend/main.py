## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## gets environment variables
## has to be done first as it actually sets the environment variables
from constants import *

## built-in libraries
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

## third-party libraries
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import HTTPBasic

## custom modules
from db.base import Base, engine, SessionLocal
from db.common import initialize_database_schema

from recurrent.scheduler import start_scheduler

from routes.warmups import router as warmups_router
from routes.kairyou import router as kairyou_router
from routes.easytl import router as easytl_router
from routes.elucidate import router as elucidate_router
from routes.auth import router as auth_router
from routes.turnstile import router as turnstile_router
from routes.db import router as db_router
from routes.financial import router as financial_router
from routes.email import router as email_router
from routes.personal import router as personal_router
from kairyou_runtime import shutdown_kairyou_worker
from request_limits import MAX_REQUEST_BODY_BYTES, RequestBodyLimitMiddleware

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------

if(not os.path.exists("database") and ACCESS_TOKEN_SECRET == "secret"):
    os.makedirs("database", exist_ok=True)

elif(not os.path.exists("database") and ACCESS_TOKEN_SECRET != "secret"):
    raise NotImplementedError("Database volume not attached and running in production mode, please exit and attach the volume")

security = HTTPBasic()

if(not os.path.exists(BACKUP_LOGS_DIR)):
    os.makedirs(BACKUP_LOGS_DIR, exist_ok=True)

envs = {
    "TURNSTILE_SECRET_KEY": TURNSTILE_SECRET_KEY,
    "ENCRYPTION_KEY": ENCRYPTION_KEY,
    "ADMIN_USER": ADMIN_USER,
    "ADMIN_PASS_HASH": ADMIN_PASS_HASH,
    "ACCESS_TOKEN_SECRET": ACCESS_TOKEN_SECRET,
    "REFRESH_TOKEN_SECRET": REFRESH_TOKEN_SECRET,
    "V1_KAIRYOU_ROOT_KEY": V1_KAIRYOU_ROOT_KEY,
    "V1_EASYTL_ROOT_KEY": V1_EASYTL_ROOT_KEY,
    "V1_EASYTL_PUBLIC_API_KEY": V1_EASYTL_PUBLIC_API_KEY,
    "V1_ELUCIDATE_ROOT_KEY": V1_ELUCIDATE_ROOT_KEY,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "STRIPE_API_KEY": STRIPE_API_KEY,
}

for key, value in envs.items():
    assert value, f"{key} environment variable not set"

initialize_database_schema(engine, Base, DATABASE_PATH)

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    del request
    safe_errors = [
        {
            key: validation_error[key]
            for key in ("type", "loc", "msg")
            if key in validation_error
        }
        for validation_error in error.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": safe_errors})

ALLOWED_CORS_ORIGINS = [
    "https://kakusui.org",
    "https://kakusui-org.pages.dev",
    "https://easytl-frontend.pages.dev",
    "https://easytl.org",
]

if ENVIRONMENT == "development":
    ALLOWED_CORS_ORIGINS.append("http://localhost:5173")


def is_allowed_cors_origin(origin: str | None) -> bool:
    return origin in ALLOWED_CORS_ORIGINS


## CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def dynamic_cors(request: Request, call_next):
    origin = request.headers.get("Origin")
    response = await call_next(request)
    if is_allowed_cors_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response.headers.add_vary_header("Origin")
    return response

class XFrameOptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['Content-Security-Policy'] = "frame-ancestors 'none';"
        return response

app.add_middleware(CSPMiddleware)
app.add_middleware(XFrameOptionsMiddleware)
app.add_middleware(
    RequestBodyLimitMiddleware,
    max_body_size=MAX_REQUEST_BODY_BYTES,
)

app.include_router(warmups_router)
app.include_router(kairyou_router)
app.include_router(easytl_router)
app.include_router(auth_router)
app.include_router(elucidate_router)
app.include_router(turnstile_router)
app.include_router(db_router)
app.include_router(financial_router)
app.include_router(personal_router)
app.include_router(email_router)

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    app.state.scheduler = await start_scheduler(db)

@app.on_event("shutdown")
async def shutdown_event():
    shutdown_kairyou_worker()
