## Copyright Kakusui LLC 2024 (https://kakusui.org) (https://github.com/Kakusui)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## built-in libraries
from logging.handlers import RotatingFileHandler

import os
import json
import logging

## third-party libraries
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from kairyou import Kairyou
from kairyou.exceptions import InvalidReplacementJsonKeys, InvalidReplacementJsonName, SpacyModelNotFound

## Define Pydantic models
class KairyouRequest(BaseModel):
    textToPreprocess: str
    replacementsJson: str

##-------------------start-of-setup_app()---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def setup_app(app: FastAPI) -> None:

    ## Load Environment Variables
    load_dotenv()

    ## Setup logging
    if(not os.path.exists('logs')):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/myapp.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))

    file_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(file_handler)

    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Application Startup')

##-----------------------------------------start-of-main----------------------------------------------------------------------------------------------------------------------------------------------------------

app = FastAPI()

## Setup the app
setup_app(app)

## CORS setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## Routes

## API Endpoints
@app.get("/")
async def api_home():
    return {"message": "Welcome to the API"}

@app.post("/v1/kairyou")
async def kairyou(request_data: KairyouRequest, request: Request):

    ## API key validation
    api_key = request.headers.get('Authorization')
    if(not api_key or api_key != os.getenv('ROOT_API_KEY')):
        raise HTTPException(status_code=401, detail="Unauthorized")

    ## kairyou receives a POST request with a JSON payload (textToPreprocess) and (replacementsJson)
    ## it returns a JSON response with the preprocessed text, preprocessing log, and error log
    ## Possible status codes: 200, 400, 405, 500, 401

    text_to_preprocess = request_data.textToPreprocess
    replacements_json = request_data.replacementsJson

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

## Under no circumstances should the app be run in production without a WSGI server
## EVER. This is only for development purposes.
## See: serve.py for production deployment.
if(__name__ == '__main__'):
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug", reload=True)
