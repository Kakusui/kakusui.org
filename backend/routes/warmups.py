## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()        

@router.get("/", status_code=status.HTTP_200_OK)
async def api_home():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Welcome to the API"}
    )

@router.get("/v1/kairyou", status_code=status.HTTP_200_OK)
async def kairyou_warm_up():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Kairyou is running."}
    )

@router.get("/v1/easytl", status_code=status.HTTP_200_OK)
async def easytl_warm_up():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "EasyTL is running."}
    )

@router.get("/v1/elucidate", status_code=status.HTTP_200_OK)
async def elucidate_warm_up():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Elucidate is running."}
    )