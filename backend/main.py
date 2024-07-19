## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
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

from easytl import EasyTL

from elucidate import Elucidate, __version__ as ELUCIDATE_VERSION

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
V1_EASYTL_ROOT_KEY = os.environ.get("V1_EASYTL_ROOT_KEY")
V1_ELUCIDATE_ROOT_KEY = os.environ.get("V1_ELUCIDATE_ROOT_KEY")

## Turnstile verification endpoint won't be used if the secret key is not set
## but for the other endpoints, we need to make sure the root keys are set
if(not any([V1_KAIRYOU_ROOT_KEY, V1_EASYTL_ROOT_KEY, V1_ELUCIDATE_ROOT_KEY])):
    get_env_variables()
    V1_KAIRYOU_ROOT_KEY = os.environ.get("V1_KAIRYOU_ROOT_KEY")
    V1_EASYTL_ROOT_KEY = os.environ.get("V1_EASYTL_ROOT_KEY")
    V1_ELUCIDATE_ROOT_KEY = os.environ.get("V1_ELUCIDATE_ROOT_KEY")

assert V1_KAIRYOU_ROOT_KEY, "V1_KAIRYOU_ROOT_KEY is not set in the environment variables"
assert V1_EASYTL_ROOT_KEY, "V1_EASYTL_ROOT_KEY is not set in the environment variables"
assert V1_ELUCIDATE_ROOT_KEY, "V1_ELUCIDATE_ROOT_KEY is not set in the environment variables"

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

    MAX_TEXT_LENGTH = 10000
    MAX_INSTRUCTIONS_LENGTH = 1000
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

    MAX_TEXT_LENGTH = 10000
    MAX_INSTRUCTIONS_LENGTH = 1000
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