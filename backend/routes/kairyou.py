## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import logging
## third-party imports
from fastapi import APIRouter, status, Request, Depends
from fastapi.responses import JSONResponse

import httpx

## custom imports
from routes.models import KairyouRequest

from constants import V1_KAIRYOU_ROOT_KEY

from auth.util import check_internal_request
from routes.turnstile import verify_turnstile_token

from util import get_backend_url, KairyouCache
from kairyou_runtime import (
    InvalidKairyouPayload,
    KAIRYOU_EXECUTION_TIMEOUT_SECONDS,
    KairyouBusyError,
    KairyouExecutionTimeout,
    KairyouProcessingError,
    KairyouWorkerError,
    parse_and_validate_replacements,
    preprocess_in_worker,
)

from sqlalchemy.orm import Session
from sqlalchemy import update
from db.base import get_db
from db.models import EndpointStats

router = APIRouter()

@router.post("/v1/kairyou")
async def kairyou(request_data:KairyouRequest, request:Request, db: Session = Depends(get_db)):
    text_to_preprocess = request_data.textToPreprocess
    replacements_json = request_data.replacementsJson
    
    api_key = request.headers.get("X-API-Key")

    if(api_key != V1_KAIRYOU_ROOT_KEY):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": "Invalid endpoint API key. If you are actually interested in using this endpoint, please contact us at contact@kakusui.org."
            }
        )

    try:
        replacements = parse_and_validate_replacements(
            replacements_json,
            text_to_preprocess,
        )
    except InvalidKairyouPayload as error:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(error)},
        )
    
    ## Update endpoint stats
    db.execute(update(EndpointStats).where(EndpointStats.endpoint == "Kairyou").values(count=EndpointStats.count + 1))
    db.commit()

    try:
        recycle_worker = KairyouCache.should_unload_model()
        preprocessed_text, preprocessing_log, error_log = await preprocess_in_worker(
            text_to_preprocess,
            replacements,
            recycle_worker=recycle_worker,
        )

        KairyouCache.mark_request_processed()
        KairyouCache.mark_model_loaded()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "preprocessedText": preprocessed_text,
                "preprocessingLog": preprocessing_log,
                "errorLog": error_log
            }
        )

    except KairyouBusyError:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"message": "Kairyou is busy. Please retry shortly."},
            headers={"Retry-After": "2"},
        )
    except KairyouExecutionTimeout:
        KairyouCache.mark_model_unloaded()
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"message": "Kairyou processing exceeded the time limit."},
        )
    except KairyouWorkerError:
        KairyouCache.mark_model_unloaded()
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"message": "Kairyou processing is temporarily unavailable."},
        )
    except KairyouProcessingError as error:
        if error.error_type == "ResourceLimit":
            KairyouCache.mark_request_processed()
            KairyouCache.mark_model_loaded()
        else:
            KairyouCache.mark_model_unloaded()
        if error.error_type in {"InvalidReplacementJsonKeys", "InvalidReplacementJsonName"}:
            response_status = status.HTTP_400_BAD_REQUEST
            message = "The replacement JSON is invalid."
        elif error.error_type == "SpacyModelNotFound":
            response_status = status.HTTP_503_SERVICE_UNAVAILABLE
            message = "The Kairyou language model is unavailable."
        elif error.error_type in {"MemoryError", "OverflowError", "ResourceLimit"}:
            response_status = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            message = "Kairyou output exceeded the configured resource limit."
        else:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            message = "An unexpected error occurred during text preprocessing."

        logging.warning("Kairyou worker rejected a request: %s", error.error_type)
        return JSONResponse(status_code=response_status, content={"message": message})
    except Exception:
        logging.exception("Unexpected Kairyou route failure")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An unexpected error occurred during text preprocessing."},
        )
    
@router.post("/proxy/kairyou")
async def proxy_kairyou(request_data:KairyouRequest, request:Request):

    await check_internal_request(request)
    await verify_turnstile_token(request_data.turnstile_token, request, "kairyou")

    timeout = httpx.Timeout(KAIRYOU_EXECUTION_TIMEOUT_SECONDS + 5.0, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_KAIRYOU_ROOT_KEY
        }
        
        try:
            response = await client.post(
                f"{await get_backend_url()}/v1/kairyou",
                json=request_data.model_dump(exclude={"turnstile_token"}),
                headers=headers
            )
            
            try:
                content = response.json()
            except ValueError:
                logging.error(f"Non-JSON response from Kairyou service: {response.status_code} - {response.text[:200]}")
                content = {
                    "message": "Service temporarily unavailable due to memory constraints",
                    "error": f"HTTP {response.status_code}: The preprocessing service is experiencing high memory usage"
                }
                return JSONResponse(status_code=503, content=content)
                
            return JSONResponse(status_code=response.status_code, content=content)
            
        except httpx.RequestError as e:
            logging.error(f"Request error calling Kairyou service: {str(e)}")
            return JSONResponse(
                status_code=503,
                content={
                    "message": "Unable to connect to preprocessing service",
                    "error": "Service temporarily unavailable"
                }
            )
