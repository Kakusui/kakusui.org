## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import json
import asyncio
import psutil
import logging
## third-party imports
from fastapi import APIRouter, status, Request, Depends
from fastapi.responses import JSONResponse

import httpx

from kairyou import Kairyou
from kairyou.exceptions import InvalidReplacementJsonKeys, InvalidReplacementJsonName, SpacyModelNotFound

## custom imports
from routes.models import KairyouRequest

from constants import V1_KAIRYOU_ROOT_KEY

from auth.util import check_internal_request

from util import get_backend_url, KairyouCache

from sqlalchemy.orm import Session
from sqlalchemy import update
from db.base import get_db
from db.models import EndpointStats

router = APIRouter()

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

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

    if(len(text_to_preprocess) > 175000):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "The text to preprocess is too long. Please keep it under 175,000 characters."
            }
        )

    memory_before = get_memory_usage()
    logging.info(f"Memory usage before Kairyou processing: {memory_before:.2f} MB")
    
    ## Update endpoint stats
    db.execute(update(EndpointStats).where(EndpointStats.endpoint == "Kairyou").values(count=EndpointStats.count + 1))
    db.commit()

    try:
        replacements_json = await asyncio.to_thread(json.loads, replacements_json)

        if(KairyouCache.should_unload_model()):
            logging.info("Kairyou model timeout reached – unloading SpaCy model from memory")
            try:
                from kairyou import Kairyou as _K
                if(hasattr(_K, "_ner")):
                    _K._ner = None
                    logging.info("SpaCy model reference cleared")
            except Exception as unload_err:
                logging.error(f"Error while unloading SpaCy model: {unload_err}")
            KairyouCache.mark_model_unloaded()

        # Always keep the model resident once loaded to avoid AttributeError on second call
        persist_model = True
        discard_ner = False

        cache_status = KairyouCache.get_status()
        logging.info(f"Starting Kairyou processing – Cache status: {cache_status}")
        logging.info(f"Calling Kairyou.preprocess(persist={persist_model}, discard_ner_objects={discard_ner})")

        preprocessed_text, preprocessing_log, error_log = await asyncio.to_thread(
            Kairyou.preprocess,
            text_to_preprocess,
            replacements_json,
            persist=persist_model,
            discard_ner_objects=discard_ner
        )

        KairyouCache.mark_request_processed()
        KairyouCache.mark_model_loaded()
        
        memory_after = get_memory_usage()
        logging.info(f"Memory usage after Kairyou processing: {memory_after:.2f} MB")
        logging.info(f"Processing completed successfully without model persistence")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "preprocessedText": preprocessed_text,
                "preprocessingLog": preprocessing_log,
                "errorLog": error_log
            }
        )

    except (InvalidReplacementJsonKeys, InvalidReplacementJsonName):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "You have an invalid replacement json file. Please see https://github.com/Bikatr7/Kairyou?tab=readme-ov-file#kairyou for what the replacement json file should look like."
            }
        )

    except SpacyModelNotFound:
        return JSONResponse(    
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An internal error occurred regarding the spacy model. Please contact the administrator at contact@kakusui.org."
            }
        )
    
    except MemoryError:
        logging.error("Memory error during Kairyou processing - likely OOM")
        return JSONResponse(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            content={
                "message": "Insufficient memory to process this request. Please try with smaller text or contact support."
            }
        )
    
    except Exception as e:
        logging.error(f"Unexpected error in Kairyou processing: {str(e)}")
        logging.error(f"Exception type: {type(e).__name__}")
        logging.error(f"Exception args: {e.args}")
        
        import traceback
        logging.error(f"Full traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error occurred during text preprocessing.",
                "error": str(e) if logging.getLogger().isEnabledFor(logging.DEBUG) else "Internal server error",
                "error_type": type(e).__name__
            }
        )
    
@router.post("/proxy/kairyou")
async def proxy_kairyou(request_data:KairyouRequest, request:Request):

    await check_internal_request(request)

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_KAIRYOU_ROOT_KEY
        }
        
        try:
            response = await client.post(f"{await get_backend_url()}/v1/kairyou", json=request_data.model_dump(), headers=headers)
            
            try:
                content = response.json()
            except (ValueError, json.JSONDecodeError):
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