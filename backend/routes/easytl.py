## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse
import logging

from easytl import EasyTL

import httpx

## custom imports
from routes.models import EasyTLRequest, TokenCostRequest

from constants import V1_EASYTL_ROOT_KEY, V1_EASYTL_PUBLIC_API_KEY

from auth.util import check_internal_request
from auth.func import get_admin_api_key, check_if_admin_user, get_current_user

from util import get_backend_url

from sqlalchemy.orm import Session
from sqlalchemy import update

from db.base import get_db
from db.models import User

router = APIRouter()

logger = logging.getLogger(__name__)

## Define the model costs
MODEL_COSTS = {
    'gpt-3.5-turbo': 0.040,
    'gpt-4': 0.700,
    'gpt-4-turbo': 0.700,
    'gpt-4o': 0.250,
    'gpt-4o-mini': 0.015,
    'gemini-1.0-pro': 0.040,
    'gemini-1.5-pro': 0.130,
    'gemini-1.5-flash': 0.009,
    'claude-3-haiku-20240307': 0.030,
    'claude-3-sonnet-20240229': 0.332,
    'claude-3-5-sonnet-20240620': 0.332,
    'claude-3-opus-20240229': 1.660
}

@router.post("/v1/easytl")
async def easytl(request_data:EasyTLRequest, request:Request, is_admin:bool = Depends(check_if_admin_user), db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):

    text_to_translate = request_data.textToTranslate
    translation_instructions = request_data.translationInstructions
    llm_type = request_data.llmType.lower()
    user_api_key = request_data.userAPIKey
    model = request_data.model
    using_credits = request_data.using_credits

    admin_api_key = await get_admin_api_key(llm_type)

    api_key = request.headers.get("X-API-Key")

    MAX_TEXT_LENGTH = 100000
    MAX_INSTRUCTIONS_LENGTH = 5000
    VALID_LLM_TYPES = ["anthropic", "openai", "gemini"]

    ERRORS = {
        "invalid_api_key": {"status_code": status.HTTP_401_UNAUTHORIZED, "content": {"message": "Invalid endpoint API key. If you are actually interested in using this endpoint, please contact us at contact@kakusui.org."}},
        "text_too_long": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "The text to translate is too long. Please keep it under 10,000 characters."}},
        "instructions_too_long": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "The translation instructions are too long. Please keep it under 1,000 characters."}},
        "invalid_llm_type": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "Invalid LLM type. Please use 'anthropic', 'openai', or 'gemini'."}},
        "invalid_user_api_key": {"status_code": status.HTTP_401_UNAUTHORIZED, "content": {"message": "Invalid user API key. Please check your credentials."}},
        "internal_error": {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "content": {"message": "An internal error occurred. Please try again later."}},
        "not_enough_credits": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "Not enough credits. Please top up your credits."}},
        "invalid_user": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "Invalid user."}}
    }

    ## these models don't listen to translation instructions well, so we need to do something different
    ## what we do is put the instructions in the text to translate
    unsophisticated_models_whitelist = [
        "gpt-3.5-turbo",
        "claude-3-haiku-20240307", 
        "claude-3-sonnet-20240229", 
        "claude-3-opus-20240229"
    ]

    if(api_key not in [V1_EASYTL_ROOT_KEY, V1_EASYTL_PUBLIC_API_KEY] and not is_admin):
        return JSONResponse(**ERRORS["invalid_api_key"])
    
    if(len(text_to_translate) > MAX_TEXT_LENGTH):
        return JSONResponse(**ERRORS["text_too_long"])
    
    if(len(translation_instructions) > MAX_INSTRUCTIONS_LENGTH):
        return JSONResponse(**ERRORS["instructions_too_long"])
        
    if(llm_type not in VALID_LLM_TYPES):
        return JSONResponse(**ERRORS["invalid_llm_type"])
    
    user = None
    number_of_characters = 0
    
    if(using_credits):

        user_api_key = admin_api_key

        number_of_characters = len(text_to_translate) + len(translation_instructions)
        user = db.query(User).filter(User.email == current_user).first()
        if(not user):
            return JSONResponse(**ERRORS["invalid_user"])
        
        number_of_credits = user.credits

        if(number_of_credits < number_of_characters): # type: ignore (IT'S FUCKING LYING)
            return JSONResponse(**ERRORS["not_enough_credits"])

    try:
        if(is_admin):
            EasyTL.set_credentials(api_type=llm_type, credentials=admin_api_key) # type: ignore
        else:
            EasyTL.set_credentials(api_type=llm_type, credentials=user_api_key) # type: ignore
        
        EasyTL.test_credentials(api_type=llm_type) # type: ignore

    except:
        return JSONResponse(**ERRORS["invalid_user_api_key"])

    try:
        if(model in unsophisticated_models_whitelist):
            text_to_translate = f"{translation_instructions}\n{text_to_translate}"
            translation_instructions = "Your instructions are in the other text."

        total_chars = len(text_to_translate) + len(translation_instructions)
        
        if(model not in MODEL_COSTS):
            return JSONResponse(**ERRORS["invalid_model"])

        cost = total_chars * MODEL_COSTS.get(model) # type: ignore

        translated_text = await EasyTL.translate_async(text=text_to_translate, 
                                                       service=llm_type, # type: ignore 
                                                       translation_instructions=translation_instructions,
                                                       model=model
                                                       ) 

        if(using_credits and user):
            new_credits = user.credits - cost
            db.execute(update(User).where(User.id == user.id).values(credits=new_credits))
            db.commit()

    except:
        return JSONResponse(**ERRORS["internal_error"])

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "translatedText": translated_text,
        "credits": user.credits if user else -1,
        "cost": cost
    })

@router.post("/v1/calculate-token-cost")
async def calculate_token_cost(request_data: TokenCostRequest):
    total_chars = len(request_data.text_to_translate) + len(request_data.translation_instructions)

    if(request_data.model not in MODEL_COSTS):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Invalid model"})
    
    cost = total_chars * MODEL_COSTS.get(request_data.model) # type: ignore

    return JSONResponse(status_code=status.HTTP_200_OK, content={"cost": cost})

@router.post("/proxy/calculate-token-cost")
async def proxy_calculate_token_cost(request_data: TokenCostRequest, request: Request):

    await check_internal_request(request)

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_EASYTL_ROOT_KEY,
            "Authorization": request.headers.get("Authorization")
        }
        response = await client.post(f"{await get_backend_url()}/v1/calculate-token-cost", json=request_data.model_dump(), headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())
    
@router.post("/proxy/easytl")
async def proxy_easytl(request_data:EasyTLRequest, request:Request):

    await check_internal_request(request)

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_EASYTL_ROOT_KEY,
            "Authorization": request.headers.get("Authorization")
        }
        response = await client.post(f"{await get_backend_url()}/v1/easytl", json=request_data.model_dump(), headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())