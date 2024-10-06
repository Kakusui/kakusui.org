## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from elucidate import Elucidate, __version__ as ELUCIDATE_VERSION

from easytl import EasyTL

import httpx

## custom imports
from routes.models import ElucidateRequest

from constants import V1_ELUCIDATE_ROOT_KEY

from auth.util import check_internal_request

from util import get_backend_url

router = APIRouter()

@router.post("/v1/elucidate")
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
        "invalid_api_key": {"status_code": status.HTTP_401_UNAUTHORIZED, "content": {"message": "Invalid endpoint API key. If you are actually interested in using this endpoint, please contact us at contact@kakusui.org."}},
        "text_too_long": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "The text to evaluate is too long. Please keep it under 10,000 characters."}},
        "instructions_too_long": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "The evaluation instructions are too long. Please keep it under 1,000 characters."}},
        "invalid_llm_type": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": f"Invalid LLM type. As of Elucidate {ELUCIDATE_VERSION}, only 'openai', 'anthropic', and 'gemini' are supported."}},
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

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "evaluatedText": evaluated_text
    })

    
@router.post("/proxy/elucidate")
async def proxy_elucidate(request_data:ElucidateRequest, request:Request):

    await check_internal_request(request)

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_ELUCIDATE_ROOT_KEY
        }
        response = await client.post(f"{await get_backend_url()}/v1/elucidate", json=request_data.model_dump(), headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())