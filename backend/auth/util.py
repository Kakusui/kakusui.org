## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import os
import asyncio

## third-party imports
from fastapi import HTTPException

from werkzeug.utils import secure_filename

## custom modules
from constants import ENVIRONMENT

async def get_secure_path(base_dir:str, filename:str) -> str:
    secure_name = await get_secure_filename(filename)
    return os.path.join(base_dir, secure_name)

async def get_secure_filename(filename:str) -> str:
    return await asyncio.to_thread(secure_filename, filename)

async def check_internal_request(origin:str | None) -> None:

    """

    Check if the request is from an internal source

    Args:
    origin (str): The origin of the request

    """

    allowed_domains = [
        "https://kakusui.org", 
        "http://localhost:5173",
        ".kakusui-org.pages.dev"
    ]

    if(ENVIRONMENT != "development"):
        allowed_domains.pop(allowed_domains.index("http://localhost:5173"))

    if(origin is None or (origin is not None and not any(origin.endswith(domain) for domain in allowed_domains))):
        raise HTTPException(status_code=403, detail="Forbidden")