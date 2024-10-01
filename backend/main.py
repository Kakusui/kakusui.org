## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## gets environment variables
## has to be done first as it actually sets the environment variables
from constants import *

## built-in libraries
import os
import threading

maintenance_mode = False
maintenance_lock = threading.Lock()

## third-party libraries
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic

## custom modules
from db.base import Base, engine, SessionLocal
from db.common import create_tables_if_not_exist
from db.migration import migrate_database

from recurrent.scheduler import start_scheduler

from routes.warmups import router as warmups_router
from routes.kairyou import router as kairyou_router
from routes.easytl import router as easytl_router
from routes.elucidate import router as elucidate_router
from routes.auth import router as auth_router
from routes.turnstile import router as turnstile_router
from routes.db import router as db_router

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
    "GEMINI_API_KEY": GEMINI_API_KEY
}

for key, value in envs.items():
    assert value, f"{key} environment variable not set"

create_tables_if_not_exist(engine, Base)

migrate_database(engine)

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------

app = FastAPI()

## CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def maintenance_middleware(request:Request, call_next):
    global maintenance_mode, maintenance_lock
    with maintenance_lock:
        if(maintenance_mode):
            return JSONResponse(status_code=503, content={"message": "Server is in maintenance mode"})
        
    response = await call_next(request)
    return response

@app.middleware("http")
async def dynamic_cors(request: Request, call_next):
    origin = request.headers.get("Origin")
    response = await call_next(request)
    if(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    return response

app.include_router(warmups_router)
app.include_router(kairyou_router)
app.include_router(easytl_router)
app.include_router(auth_router)
app.include_router(elucidate_router)
app.include_router(turnstile_router)
app.include_router(db_router)

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    app.state.scheduler = await start_scheduler(db)

@app.on_event("shutdown")
async def shutdown_event():
    scheduler = app.state.scheduler
    if scheduler:
        scheduler.shutdown(wait=False)