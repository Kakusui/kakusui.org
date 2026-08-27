## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import asyncio
from urllib.parse import urlsplit

## third-party imports
from fastapi import HTTPException, Request

from werkzeug.utils import secure_filename

## custom modules
from constants import ENVIRONMENT

async def get_secure_path(base_dir:str, filename:str) -> str:
    secure_name = await get_secure_filename(filename)
    return os.path.join(base_dir, secure_name)

async def get_secure_filename(filename:str) -> str:
    return await asyncio.to_thread(secure_filename, filename)

async def check_internal_request(request:Request) -> None:
    """
    Enforce the browser origin allowlist as a CSRF/CORS defense.

    Origin is client-controlled outside a browser and must never be treated as
    authentication. Sensitive callers need an independent bearer, admin, or
    Turnstile check.
    """
    allowed_origins = {
        "https://kakusui.org", 
        "https://kakusui-org.pages.dev",
        "https://easytl-frontend.pages.dev",
        "https://easytl.org"
    }

    origin = request.headers.get('origin')
    
    if(ENVIRONMENT == "development"):
        allowed_origins.add("http://localhost:5173")

    if(origin is None):
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        parsed_origin = urlsplit(origin)
        parsed_origin.port
    except ValueError:
        raise HTTPException(status_code=403, detail="Forbidden")

    if(parsed_origin.path or parsed_origin.query or parsed_origin.fragment or parsed_origin.username or parsed_origin.password):
        raise HTTPException(status_code=403, detail="Forbidden")

    normalized_origin = f"{parsed_origin.scheme.lower()}://{parsed_origin.netloc.lower()}"
    if(normalized_origin not in allowed_origins):
        raise HTTPException(status_code=403, detail="Forbidden")
    
async def is_safe_filename(filename:str) -> bool:
    return await asyncio.to_thread(lambda: '..' not in filename and filename == os.path.basename(filename))
