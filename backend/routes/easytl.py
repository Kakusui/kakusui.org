## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.background import BackgroundTask
import logging
import json
import traceback

from easytl import EasyTL

import httpx

## custom imports
from routes.models import EasyTLRequest, TokenCostRequest, LanguageDetectionRequest

from constants import V1_EASYTL_ROOT_KEY, V1_EASYTL_PUBLIC_API_KEY

from auth.util import check_internal_request
from auth.func import get_admin_api_key, check_if_admin_user, get_current_user
from routes.turnstile import verify_turnstile_token

from util import get_backend_url

from sqlalchemy.orm import Session
from sqlalchemy import update

from db.base import get_db, SessionLocal
from db.credit_accounting import (
    CreditReservation,
    CreditReservationStatus,
    refund_credits,
    reserve_credits,
)
from db.models import EndpointStats
from llm_provider_lock import get_llm_provider_lock

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

MODEL_SERVICES = {
    'gpt-3.5-turbo': 'openai',
    'gpt-4': 'openai',
    'gpt-4-turbo': 'openai',
    'gpt-4o': 'openai',
    'gpt-4o-mini': 'openai',
    'gemini-1.0-pro': 'gemini',
    'gemini-1.5-pro': 'gemini',
    'gemini-1.5-flash': 'gemini',
    'claude-3-haiku-20240307': 'anthropic',
    'claude-3-sonnet-20240229': 'anthropic',
    'claude-3-5-sonnet-20240620': 'anthropic',
    'claude-3-opus-20240229': 'anthropic',
}

MAX_TEXT_LENGTH = 100000
MAX_INSTRUCTIONS_LENGTH = 5000
MAX_TRANSLATION_OUTPUT_TOKENS = 4096
MIN_TRANSLATION_OUTPUT_TOKENS = 64
LANGUAGE_DETECTION_OUTPUT_TOKENS = 16
VALID_LLM_TYPES = ["anthropic", "openai", "gemini"]
LANGUAGE_DETECTION_PROMPT = (
    "You are a language detection expert. Your only task is to detect the language of the "
    "following text and respond with ONLY the language name in English. For example, if the "
    "text is in Japanese, just respond with 'Japanese'. Here's the text:\n\n"
)
LANGUAGE_DETECTION_INSTRUCTIONS = "Respond with ONLY the language name in English. No additional text."

ERRORS = {
    "invalid_api_key": {"status_code": status.HTTP_401_UNAUTHORIZED, "content": {"message": "Invalid endpoint API key. If you are actually interested in using this endpoint, please contact us at contact@kakusui.org."}},
    "text_too_long": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "The text to translate is too long. Please keep it under 10,000 characters."}},
    "instructions_too_long": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "The translation instructions are too long. Please keep it under 1,000 characters."}},
    "invalid_llm_type": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "Invalid LLM type. Please use 'anthropic', 'openai', or 'gemini'."}},
    "invalid_user_api_key": {"status_code": status.HTTP_401_UNAUTHORIZED, "content": {"message": "Invalid user API key. Please check your credentials."}},
    "internal_error": {"status_code": status.HTTP_500_INTERNAL_SERVER_ERROR, "content": {"message": "An internal error occurred. Please try again later."}},
    "not_enough_credits": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "Not enough credits. Please top up your credits."}},
    "invalid_user": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "Invalid user."}},
    "invalid_model": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "Invalid model for the selected LLM type."}},
    "empty_credit_request": {"status_code": status.HTTP_400_BAD_REQUEST, "content": {"message": "Credit-funded requests must contain text."}},
}

## these models don't listen to translation instructions well, so we need to do something different
## what we do is put the instructions in the text to translate
unsophisticated_models_whitelist = [
    "gpt-3.5-turbo",
    "claude-3-haiku-20240307", 
    "claude-3-sonnet-20240229", 
    "claude-3-opus-20240229"
]


def _prepare_translation_payload(text: str, instructions: str, model: str) -> tuple[str, str]:
    if(model in unsophisticated_models_whitelist):
        return f"{instructions}\n{text}", "Your instructions are in the other text."
    return text, instructions


def _prepare_language_detection_payload(text: str) -> tuple[str, str]:
    return f"{LANGUAGE_DETECTION_PROMPT}{text}", LANGUAGE_DETECTION_INSTRUCTIONS


def _calculate_credit_cost(text: str, instructions: str, model: str) -> float:
    return (len(text) + len(instructions)) * MODEL_COSTS[model]


def _translation_output_token_limit(source_text: str) -> int:
    return min(
        MAX_TRANSLATION_OUTPUT_TOKENS,
        max(MIN_TRANSLATION_OUTPUT_TOKENS, len(source_text) * 2),
    )


def _output_limit_kwargs(llm_type: str, output_tokens: int) -> dict[str, int]:
    if(llm_type == "openai"):
        return {"max_tokens": output_tokens}
    return {"max_output_tokens": output_tokens}


def _model_matches_service(model: str, llm_type: str) -> bool:
    return MODEL_SERVICES.get(model) == llm_type


def _configure_credentials(
    llm_type: str,
    user_api_key: str,
    admin_api_key: str | None,
    using_credits: bool,
    is_admin: bool,
) -> bool:
    credentials = admin_api_key if using_credits or is_admin else user_api_key
    try:
        EasyTL.set_credentials(api_type=llm_type, credentials=credentials)  # type: ignore
        if not using_credits and not is_admin:
            EasyTL.test_credentials(api_type=llm_type)  # type: ignore
    except Exception:
        return False
    return True


def _reserve_request_credits(db: Session, email: str, cost: float) -> CreditReservation | JSONResponse:
    try:
        reservation = reserve_credits(db, email, cost)
    except Exception:
        db.rollback()
        logger.exception("Unable to reserve EasyTL credits")
        return JSONResponse(**ERRORS["internal_error"])

    if reservation.status == CreditReservationStatus.INVALID_USER:
        return JSONResponse(**ERRORS["invalid_user"])
    if reservation.status == CreditReservationStatus.INSUFFICIENT_CREDITS:
        return JSONResponse(**ERRORS["not_enough_credits"])
    return reservation


def _refund_request_credits(db: Session, reservation: CreditReservation, cost: float) -> float | None:
    try:
        return refund_credits(db, reservation.user_id, cost)
    except Exception:
        db.rollback()
        logger.exception("Unable to refund an unused EasyTL credit reservation")
        return None


def _record_endpoint_call(db: Session) -> None:
    try:
        db.execute(update(EndpointStats).where(EndpointStats.endpoint == "EasyTL").values(count=EndpointStats.count + 1))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Unable to update EasyTL endpoint statistics")

@router.post("/v1/easytl")
async def easytl(request_data:EasyTLRequest, request:Request, is_admin:bool = Depends(check_if_admin_user), db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):

    text_to_translate = request_data.textToTranslate
    translation_instructions = request_data.translationInstructions
    llm_type = request_data.llmType.lower()
    user_api_key = request_data.userAPIKey
    model = request_data.model
    using_credits = request_data.using_credits

    api_key = request.headers.get("X-API-Key")

    if(api_key not in [V1_EASYTL_ROOT_KEY, V1_EASYTL_PUBLIC_API_KEY] and not is_admin):
        return JSONResponse(**ERRORS["invalid_api_key"])
    
    if(len(text_to_translate) > MAX_TEXT_LENGTH):
        return JSONResponse(**ERRORS["text_too_long"])
    
    if(len(translation_instructions) > MAX_INSTRUCTIONS_LENGTH):
        return JSONResponse(**ERRORS["instructions_too_long"])
        
    if(llm_type not in VALID_LLM_TYPES):
        return JSONResponse(**ERRORS["invalid_llm_type"])
    if(not _model_matches_service(model, llm_type)):
        return JSONResponse(**ERRORS["invalid_model"])

    if(using_credits and not text_to_translate.strip()):
        return JSONResponse(**ERRORS["empty_credit_request"])
    text_to_translate, translation_instructions = _prepare_translation_payload(
        text_to_translate, translation_instructions, model
    )
    cost = _calculate_credit_cost(text_to_translate, translation_instructions, model)

    admin_api_key = await get_admin_api_key(llm_type)
    remaining_credits = -1
    async with get_llm_provider_lock(llm_type):
        if(not _configure_credentials(llm_type, user_api_key, admin_api_key, using_credits, is_admin)):
            return JSONResponse(**ERRORS["invalid_user_api_key"])

        if(using_credits):
            reservation_result = _reserve_request_credits(db, current_user, cost)
            if(isinstance(reservation_result, JSONResponse)):
                return reservation_result
            remaining_credits = reservation_result.balance

        ## Update endpoint stats if not an admin user, cause it'll be me lol
        if(not is_admin):
            _record_endpoint_call(db)

        try:
            translated_text = await EasyTL.translate_async(text=text_to_translate,
                                                           service=llm_type, # type: ignore
                                                           translation_instructions=translation_instructions,
                                                           model=model,
                                                           **_output_limit_kwargs(llm_type, _translation_output_token_limit(request_data.textToTranslate))
                                                           )

        except Exception:
            logger.error(traceback.format_exc())
            return JSONResponse(**ERRORS["internal_error"])

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "translatedText": translated_text,
        "credits": remaining_credits,
        "cost": cost
    })

@router.post("/v1/calculate-token-cost")
async def calculate_token_cost(request_data: TokenCostRequest):
    if(request_data.model not in MODEL_COSTS):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Invalid model"})

    provider_text, provider_instructions = _prepare_translation_payload(
        request_data.text_to_translate, request_data.translation_instructions, request_data.model
    )
    cost = _calculate_credit_cost(provider_text, provider_instructions, request_data.model)

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
    if(not request_data.using_credits):
        await verify_turnstile_token(request_data.turnstile_token, request, "easytl")

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_EASYTL_ROOT_KEY,
            "Authorization": request.headers.get("Authorization")
        }
        response = await client.post(
            f"{await get_backend_url()}/v1/easytl",
            json=request_data.model_dump(exclude={"turnstile_token"}),
            headers=headers
        )

        return JSONResponse(status_code=response.status_code, content=response.json())
    
@router.post("/proxy/easytl/stream")
async def proxy_easytl_stream(request_data:EasyTLRequest, request:Request):
    await check_internal_request(request)
    if(not request_data.using_credits):
        await verify_turnstile_token(request_data.turnstile_token, request, "easytl_stream")

    async def generate():
        async with httpx.AsyncClient(timeout=None) as client:
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": V1_EASYTL_ROOT_KEY,
                "Authorization": request.headers.get("Authorization")
            }
            
            async with client.stream('POST', f"{await get_backend_url()}/v1/easytl/stream", 
                                   json=request_data.model_dump(exclude={"turnstile_token"}),
                                   headers=headers) as response:
                async for line in response.aiter_lines():
                    if(line):
                        yield f"{line}\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

@router.post("/v1/easytl/stream")
async def easytl_stream(request_data:EasyTLRequest, request:Request, is_admin:bool = Depends(check_if_admin_user), db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    text_to_translate = request_data.textToTranslate
    translation_instructions = request_data.translationInstructions
    llm_type = request_data.llmType.lower()
    user_api_key = request_data.userAPIKey
    model = request_data.model
    using_credits = request_data.using_credits

    api_key = request.headers.get("X-API-Key")

    if(api_key not in [V1_EASYTL_ROOT_KEY, V1_EASYTL_PUBLIC_API_KEY] and not is_admin):
        return JSONResponse(**ERRORS["invalid_api_key"])

    if(len(text_to_translate) > MAX_TEXT_LENGTH):
        return JSONResponse(**ERRORS["text_too_long"])
    
    if(len(translation_instructions) > MAX_INSTRUCTIONS_LENGTH):
        return JSONResponse(**ERRORS["instructions_too_long"])
        
    if(llm_type not in VALID_LLM_TYPES):
        return JSONResponse(**ERRORS["invalid_llm_type"])
    if(not _model_matches_service(model, llm_type)):
        return JSONResponse(**ERRORS["invalid_model"])

    if(using_credits and not text_to_translate.strip()):
        return JSONResponse(**ERRORS["empty_credit_request"])
    text_to_translate, translation_instructions = _prepare_translation_payload(
        text_to_translate, translation_instructions, model
    )
    cost = _calculate_credit_cost(text_to_translate, translation_instructions, model)
    output_token_limit = _translation_output_token_limit(request_data.textToTranslate)

    admin_api_key = await get_admin_api_key(llm_type)
    reservation = None
    remaining_credits = -1
    if(using_credits):
        reservation_result = _reserve_request_credits(db, current_user, cost)
        if(isinstance(reservation_result, JSONResponse)):
            return reservation_result
        reservation = reservation_result
        remaining_credits = reservation.balance

    reservation_state = {"active": reservation is not None}

    async def finalize_unused_reservation() -> float | None:
        if(not reservation_state["active"] or reservation is None):
            return None

        # Fail closed if a refund itself fails; never retry and risk double-crediting.
        reservation_state["active"] = False
        with SessionLocal() as refund_db:
            refunded_balance = _refund_request_credits(refund_db, reservation, cost)
        return refunded_balance

    async def generate():
        stream_balance = remaining_credits
        provider_lock = get_llm_provider_lock(llm_type)
        provider_lock_acquired = False
        try:
            await provider_lock.acquire()
            provider_lock_acquired = True

            if(not _configure_credentials(llm_type, user_api_key, admin_api_key, using_credits, is_admin)):
                raise ValueError("Invalid user API key")

            stream = None
            if llm_type == "openai":
                reservation_state["active"] = False
                stream = await EasyTL.openai_translate_async(
                    text=text_to_translate,
                    translation_instructions=translation_instructions,
                    model=model,
                    stream=True,
                    max_tokens=output_token_limit
                )
                async for chunk in stream: # type: ignore
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        reservation_state["active"] = False
                        yield f"data: {json.dumps({'text': chunk.choices[0].delta.content})}\n\n"

            elif llm_type == "anthropic":
                reservation_state["active"] = False
                stream = await EasyTL.anthropic_translate_async(
                    text=text_to_translate,
                    translation_instructions=translation_instructions,
                    model=model,
                    stream=True,
                    max_output_tokens=output_token_limit
                )
                async for event in stream: # type: ignore
                    if event.type == "content_block_delta" and hasattr(event.delta, 'text'):
                        reservation_state["active"] = False
                        yield f"data: {json.dumps({'text': event.delta.text})}\n\n"

            elif llm_type == "gemini":
                reservation_state["active"] = False
                stream = await EasyTL.gemini_translate_async(
                    text=text_to_translate,
                    translation_instructions=translation_instructions,
                    model=model,
                    stream=True,
                    max_output_tokens=output_token_limit
                )
                async for chunk in stream: # type: ignore
                    if hasattr(chunk, 'text') and chunk.text:
                        reservation_state["active"] = False
                        yield f"data: {json.dumps({'text': chunk.text})}\n\n"

            if using_credits:
                if reservation_state["active"]:
                    refunded_balance = await finalize_unused_reservation()
                    if(refunded_balance is not None):
                        stream_balance = refunded_balance
                yield f"data: {json.dumps({'credits': stream_balance})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception:
            logging.error(traceback.format_exc())
            await finalize_unused_reservation()
            yield f"data: {json.dumps({'error': 'An internal error has occurred!'})}\n\n"
        finally:
            if(provider_lock_acquired):
                provider_lock.release()
            await finalize_unused_reservation()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        background=BackgroundTask(finalize_unused_reservation),
    )

@router.post("/v1/easytl/detect-language")
async def detect_language(request_data:LanguageDetectionRequest, request:Request, is_admin:bool = Depends(check_if_admin_user), db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    text = request_data.text
    llm_type = request_data.llmType.lower()
    user_api_key = request_data.userAPIKey
    model = request_data.model
    using_credits = request_data.using_credits

    api_key = request.headers.get("X-API-Key")

    if(api_key not in [V1_EASYTL_ROOT_KEY, V1_EASYTL_PUBLIC_API_KEY] and not is_admin):
        return JSONResponse(**ERRORS["invalid_api_key"])
    
    if(len(text) > MAX_TEXT_LENGTH):
        return JSONResponse(**ERRORS["text_too_long"])
        
    if(llm_type not in VALID_LLM_TYPES):
        return JSONResponse(**ERRORS["invalid_llm_type"])
    if(not _model_matches_service(model, llm_type)):
        return JSONResponse(**ERRORS["invalid_model"])

    if(using_credits and not text.strip()):
        return JSONResponse(**ERRORS["empty_credit_request"])
    provider_text, provider_instructions = _prepare_language_detection_payload(text)
    cost = _calculate_credit_cost(provider_text, provider_instructions, model)

    admin_api_key = await get_admin_api_key(llm_type)
    remaining_credits = -1
    async with get_llm_provider_lock(llm_type):
        if(not _configure_credentials(llm_type, user_api_key, admin_api_key, using_credits, is_admin)):
            return JSONResponse(**ERRORS["invalid_user_api_key"])

        if(using_credits):
            reservation_result = _reserve_request_credits(db, current_user, cost)
            if(isinstance(reservation_result, JSONResponse)):
                return reservation_result
            remaining_credits = reservation_result.balance

        if(not is_admin):
            _record_endpoint_call(db)

        try:
            detected_language = await EasyTL.translate_async(
                text=provider_text,
                service=llm_type, # type: ignore
                translation_instructions=provider_instructions,
                model=model,
                **_output_limit_kwargs(llm_type, LANGUAGE_DETECTION_OUTPUT_TOKENS)
            )

        except Exception:
            logger.error(traceback.format_exc())
            return JSONResponse(**ERRORS["internal_error"])

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "detectedLanguage": detected_language.strip(), # type: ignore (IT'S FUCKING LYING)
        "credits": remaining_credits,
        "cost": cost
    })

@router.post("/proxy/easytl/detect-language")
async def proxy_detect_language(request_data:LanguageDetectionRequest, request:Request):
    await check_internal_request(request)
    if(not request_data.using_credits):
        await verify_turnstile_token(request_data.turnstile_token, request, "easytl_detect")

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_EASYTL_ROOT_KEY,
            "Authorization": request.headers.get("Authorization")
        }
        response = await client.post(f"{await get_backend_url()}/v1/easytl/detect-language", 
                                   json=request_data.model_dump(exclude={"turnstile_token"}),
                                   headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())
