## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
import httpx

from fastapi import APIRouter, HTTPException, Request, status

## custom imports
from constants import TURNSTILE_SECRET_KEY

from auth.util import check_internal_request

from routes.models import VerifyTurnstileRequest

router = APIRouter()

@router.post("/auth/verify-turnstile")
async def verify_turnstile(request_data:VerifyTurnstileRequest, request:Request):

    await check_internal_request(request)

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
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Turnstile verification failed")
            
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while verifying the token")