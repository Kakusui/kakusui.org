## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import json
import asyncio
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
    
    ## Update endpoint stats
    db.execute(update(EndpointStats).where(EndpointStats.endpoint == "Kairyou").values(count=EndpointStats.count + 1))
    db.commit()

    try:
        replacements_json = await asyncio.to_thread(json.loads, replacements_json)

        should_save_memory = KairyouCache.should_save_memory()
        
        preprocessed_text, preprocessing_log, error_log = await asyncio.to_thread(
            Kairyou.preprocess, 
            text_to_preprocess, 
            replacements_json, 
            should_save_memory
        )

        KairyouCache.update_last_used()

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
    
@router.post("/proxy/kairyou")
async def proxy_kairyou(request_data:KairyouRequest, request:Request):

    await check_internal_request(request)

    async with httpx.AsyncClient(timeout=None) as client:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": V1_KAIRYOU_ROOT_KEY
        }
        response = await client.post(f"{await get_backend_url()}/v1/kairyou", json=request_data.model_dump(), headers=headers)

        return JSONResponse(status_code=response.status_code, content=response.json())