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

async def get_frontend_url(is_home_page:bool = True) -> str:

    """
    Returns the URL of the frontend based on the environment.
    """

    if(ENVIRONMENT == "development"):
        return "http://localhost:5173"
    
    if(not is_home_page):
        return "https://easytl.org"
    
    return "https://kakusui.org"

class KairyouCache:
    _last_request_time: datetime | None = None
    _model_loaded: bool = False
    _model_unload_timeout_minutes: int = 5
    
    @classmethod
    def mark_request_processed(cls):
        """Mark that a request was processed"""
        cls._last_request_time = datetime.now()
    
    @classmethod
    def mark_model_loaded(cls):
        """Mark that the NLP model is loaded in memory"""
        cls._model_loaded = True
    
    @classmethod
    def mark_model_unloaded(cls):
        """Mark that the NLP model has been unloaded from memory"""
        cls._model_loaded = False
    
    @classmethod
    def should_unload_model(cls) -> bool:
        """Check if model should be unloaded due to timeout"""
        if cls._last_request_time is None or not cls._model_loaded:
            return False
        
        time_since_last_request = datetime.now() - cls._last_request_time
        return time_since_last_request > timedelta(minutes=cls._model_unload_timeout_minutes)
    
    @classmethod
    def is_model_loaded(cls) -> bool:
        """Check if model is currently loaded"""
        return cls._model_loaded
    
    @classmethod
    def get_status(cls) -> dict:
        """Get current cache status for debugging"""
        return {
            "model_loaded": cls._model_loaded,
            "last_request": cls._last_request_time.isoformat() if cls._last_request_time else None,
            "should_unload": cls.should_unload_model(),
            "timeout_minutes": cls._model_unload_timeout_minutes
        }