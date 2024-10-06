## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## gets environment variables
## has to be done first as it actually sets the environment variables
from constants import *

## built-in libraries
import os
import asyncio
import logging

## third-party libraries
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from starlette.middleware.sessions import SessionMiddleware

## custom modules
from middleware import (
    SecurityHeadersMiddleware,
    MaintenanceMiddleware,
    DynamicCorsMiddleware,
    CsrfMiddleware,
)

from middleware import maintenance_mode, maintenance_lock

from db.base import Base, engine, SessionLocal
from db.common import create_tables_if_not_exist
from db.migration import migrate_database

from rate_limit.func import periodic_cleanup

from recurrent.scheduler import start_scheduler

from routes.warmups import router as warmups_router
from routes.kairyou import router as kairyou_router
from routes.easytl import router as easytl_router
from routes.elucidate import router as elucidate_router
from routes.auth import router as auth_router
from routes.turnstile import router as turnstile_router
from routes.db import router as db_router
from routes.financial import router as financial_router

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if(not os.path.exists("database") and ACCESS_TOKEN_SECRET == "secret"):
    os.makedirs("database", exist_ok=True)
    logger.info("In production, created database directory")

elif(not os.path.exists("database") and ACCESS_TOKEN_SECRET != "secret"):
    logger.error("Database volume not attached and running in production mode")
    raise NotImplementedError("Database volume not attached and running in production mode, please exit and attach the volume")

if(not os.path.exists(BACKUP_LOGS_DIR)):
    os.makedirs(BACKUP_LOGS_DIR, exist_ok=True)
    logger.info(f"Created backup logs directory: {BACKUP_LOGS_DIR}")

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
    if not value:
        logger.error(f"{key} environment variable not set")
        assert value, f"{key} environment variable not set"
    else:
        logger.info(f"{key} environment variable is set")

create_tables_if_not_exist(engine, Base)
logger.info("Database tables created or verified")

migrate_database(engine)
logger.info("Database migration completed")

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------

app = FastAPI()
logger.info("FastAPI application initialized")

## CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware added")

app.add_middleware(SessionMiddleware, secret_key=ACCESS_TOKEN_SECRET)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MaintenanceMiddleware)
app.add_middleware(DynamicCorsMiddleware)
app.add_middleware(CsrfMiddleware)

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

app.include_router(warmups_router)
app.include_router(kairyou_router)
app.include_router(easytl_router)
app.include_router(auth_router)
app.include_router(elucidate_router)
app.include_router(turnstile_router)
app.include_router(db_router)
app.include_router(financial_router)
logger.info("All routers included")

asyncio.create_task(periodic_cleanup())
logger.info("Periodic cleanup task created")

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    app.state.scheduler = await start_scheduler(db)
    logger.info("Application startup completed, scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler = app.state.scheduler
    if(scheduler):
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shutdown completed")
    logger.info("Application shutdown completed")