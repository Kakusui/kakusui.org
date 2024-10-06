## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## built-in libraries
import threading

## third-party libraries
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse

maintenance_mode = False
maintenance_lock = threading.Lock()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:;"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

class MaintenanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        global maintenance_mode, maintenance_lock
        with maintenance_lock:
            if(maintenance_mode):
                return JSONResponse(status_code=503, content={"message": "Server is in maintenance mode"})
        return await call_next(request)