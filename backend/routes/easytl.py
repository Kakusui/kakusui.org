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
from routes.models import EasyTLRequest

from constants import V1_EASYTL_ROOT_KEY, V1_EASYTL_PUBLIC_API_KEY

from auth.util import check_internal_request
from auth.func import get_admin_api_key, check_if_admin_user

from util import get_url

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/v1/easytl")
async def easytl(request_data:EasyTLRequest, request:Request, is_admin:bool = Depends(check_if_admin_user)):

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
        "invalid_api_key": {"status_code": status.HTTP_401_UNAUTHORIZED, "content": {"message": "Invalid endpoint API key. If you are actually interested in using this endpoint, please contact us at contact@kakusui.org."}},
        "text_too_long": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "The text to translate is too long. Please keep it under 10,000 characters."}},
        "instructions_too_long": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "The translation instructions are too long. Please keep it under 1,000 characters."}},
        "invalid_llm_type": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "Invalid LLM type. Please use 'anthropic', 'openai', or 'gemini'."}},
        "invalid_user_api_key": {"status_code": status.HTTP_401_UNAUTHORIZED, "content": {"message": "Invalid user API key. Please check your credentials."}},
        "internal_error": {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "content": {"message": "An internal error occurred. Please try again later."}}
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
    
    try:
        if(is_admin):
            admin_api_key = get_admin_api_key(llm_type)
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

        translated_text = await EasyTL.translate_async(text=text_to_translate, 
                                                       service=llm_type, # type: ignore 
                                                       translation_instructions=translation_instructions,
                                                       model=model
                                                       ) 

    except:
        return JSONResponse(**ERRORS["internal_error"])

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "translatedText": translated_text
    })

@router.post("/proxy/easytl")
async def proxy_easytl(request_data:EasyTLRequest, request:Request):
    origin = request.headers.get('origin')

    check_internal_request(origin)

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_EASYTL_ROOT_KEY,
            "Authorization": request.headers.get("Authorization")
        }
        response = await client.post(f"{get_url()}/v1/easytl", json=request_data.model_dump(), headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())