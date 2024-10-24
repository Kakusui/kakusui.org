## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

from constants import ENVIRONMENT
from datetime import datetime, timedelta

async def get_backend_url() -> str:

    """
    Returns the URL of the API based on the environment.
    """

    if(ENVIRONMENT == "development"):
        return "http://api.localhost:5000"
    
    return "https://api.kakusui.org"

async def get_frontend_url() -> str:

    """
    Returns the URL of the frontend based on the environment.
    """

    if(ENVIRONMENT == "development"):
        return "http://localhost:5173"
    
    return "https://kakusui.org"

class KairyouCache:
    _last_used: datetime | None = None
    
    @classmethod
    def update_last_used(cls):
        cls._last_used = datetime.now()
    
    @classmethod
    def should_save_memory(cls) -> bool:
        if cls._last_used is None:
            return True
        
        time_since_last_use = datetime.now() - cls._last_used
        return time_since_last_use > timedelta(seconds=30)
