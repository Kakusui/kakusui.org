## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by a GNU General Public License v3.0
## license that can be found in the LICENSE file.

## built-in libraries
import threading
import logging
## third-party libraries
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

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

class DynamicCorsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("Origin")
        
        if(request.method == "OPTIONS"):
            response = JSONResponse(content={})
        else:
            response = await call_next(request)
        
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-CSRF-TOKEN"
        
        if(request.method == "OPTIONS"):
            response.headers["Access-Control-Max-Age"] = "600"
        
        return response

class CsrfMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            csrf_protect = CsrfProtect()
            try:
                await csrf_protect.validate_csrf(request)
            except CsrfProtectError as e:
                logging.error(f"CSRF validation failed: {str(e)}")
                return JSONResponse(status_code=403, content={"detail": str(e)})
        response = await call_next(request)
        return response

def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})