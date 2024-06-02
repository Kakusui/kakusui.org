## Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## built-in libraries
import json
import os

## third-party libraries
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from kairyou import Kairyou
from kairyou.exceptions import InvalidReplacementJsonKeys, InvalidReplacementJsonName, SpacyModelNotFound

import httpx

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

##-----------------------------------------start-of-pydantic-models----------------------------------------------------------------------------------------------------------------------------------------------------------

## Define Pydantic models
class KairyouRequest(BaseModel):
    textToPreprocess: str
    replacementsJson: str

class VerifyTurnstileRequest(BaseModel):
    token: str

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------

app = FastAPI()

## CORS setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
V1_KAIRYOU_ROOT_KEY = os.environ.get("V1_KAIRYOU_ROOT_KEY")

## Turnstile verification endpoint won't be used if the secret key is not set
## but for kairyou we need to get it from env if it's not there already (cloudflare pages)
if(not V1_KAIRYOU_ROOT_KEY):
    get_env_variables()
    V1_KAIRYOU_ROOT_KEY = os.environ.get("V1_KAIRYOU_ROOT_KEY")

assert V1_KAIRYOU_ROOT_KEY, "V1_KAIRYOU_ROOT_KEY is not set in the environment variables"

## Routes

## API Endpoints
@app.get("/")
async def api_home():
    return {"message": "Welcome to the API"}

## Kairyou endpoints

@app.get("/v1/kairyou")
async def kairyou_warm_up():
    return {"message": "Kairyou is running."}

## if and when we ever actually open this up to the public, we will need to add a rate limiter

@app.post("/v1/kairyou")
async def kairyou(request_data:KairyouRequest, request:Request):
    text_to_preprocess = request_data.textToPreprocess
    replacements_json = request_data.replacementsJson
    
    api_key = request.headers.get("X-API-Key")

    if(api_key != V1_KAIRYOU_ROOT_KEY):
        return JSONResponse(status_code=401, content={
            "message": "Invalid API key. If you are actually interested in using this endpoint, please contact support@kakusui.org."
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

## EasyTL endpoints
@app.get("/v1/easytl")
async def easytl_warm_up():
    return {"message": "The endpoint is still under development."}

## Turnstile verification endpoint
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

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            result = response.json()
            
            if(result.get('success')):
                return {"success": True}
            else:
                raise HTTPException(status_code=400, detail="Turnstile verification failed")
            
    except Exception:
        raise HTTPException(status_code=500, detail="An error occurred while verifying the token")

## Proxy endpoint for Kairyou
## Used only by Kakusui.org
@app.post("/proxy/kairyou")
async def proxy_kairyou(request_data:KairyouRequest, request:Request):
    origin = request.headers.get('origin')

    if(origin not in ["https://kakusui.org", "http://localhost:5173"]):
        raise HTTPException(status_code=403, detail="Forbidden")

    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_KAIRYOU_ROOT_KEY
        }
        response = await client.post(f"{get_url()}/v1/kairyou", json=request_data.model_dump(), headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())