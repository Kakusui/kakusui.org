## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
from ipaddress import ip_address

## third-party imports
import httpx

from fastapi import APIRouter, HTTPException, Request, status

## custom imports
from auth.client import get_request_client_ip
from auth.throttle import enforce_turnstile_verification_limits
from constants import ENVIRONMENT, TURNSTILE_SECRET_KEY

router = APIRouter()

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
TURNSTILE_ACTIONS = {
    "easytl",
    "easytl_detect",
    "easytl_stream",
    "elucidate",
    "feedback",
    "kairyou",
    "verification_email",
}
TURNSTILE_HOSTNAMES = {
    "easytl-frontend.pages.dev",
    "easytl.org",
    "kakusui-org.pages.dev",
    "kakusui.org",
}
TURNSTILE_TIMEOUT = httpx.Timeout(5.0, connect=3.0)
LOCAL_DEVELOPMENT_HOSTNAMES = {"api.localhost", "localhost", "127.0.0.1", "testserver"}
def _is_allowed_hostname(hostname: object) -> bool:
    if(not isinstance(hostname, str)):
        return False

    normalized_hostname = hostname.lower().rstrip(".")
    if(normalized_hostname in TURNSTILE_HOSTNAMES):
        return True

    return ENVIRONMENT == "development" and normalized_hostname in {"localhost", "127.0.0.1", "testserver"}


def _get_client_ip(request:Request) -> str | None:
    return get_request_client_ip(request)


def _is_local_development_request(request:Request) -> bool:
    request_hostname = (request.url.hostname or "").lower().rstrip(".")
    if(request_hostname not in LOCAL_DEVELOPMENT_HOSTNAMES):
        return False

    # A Cloudflare header means this did not originate from the local dev client.
    if(request.headers.get("CF-Connecting-IP") is not None or request.client is None):
        return False

    if(request.client.host == "testclient"):
        return request_hostname == "testserver"

    try:
        peer_address = ip_address(request.client.host)
    except ValueError:
        return False

    return peer_address.is_loopback or peer_address.is_private


async def _verify_turnstile_response(
    token: str,
    request: Request,
    expected_action: str | None,
) -> None:
    if(ENVIRONMENT == "development"):
        if(_is_local_development_request(request)):
            return
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Verification service unavailable")

    if(not TURNSTILE_SECRET_KEY):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Verification service unavailable")

    data = {
        "secret": TURNSTILE_SECRET_KEY,
        "response": token,
    }
    client_ip = _get_client_ip(request)
    if(client_ip is not None):
        data["remoteip"] = client_ip

    try:
        async with httpx.AsyncClient(timeout=TURNSTILE_TIMEOUT, follow_redirects=False) as client:
            response = await client.post(TURNSTILE_VERIFY_URL, data=data)
            response.raise_for_status()
            result = response.json()
            if(not isinstance(result, dict)):
                raise ValueError("Invalid Turnstile response")
    except (httpx.HTTPError, ValueError):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Verification service unavailable")

    if(
        not result.get("success")
        or (expected_action is not None and result.get("action") != expected_action)
        or not _is_allowed_hostname(result.get("hostname"))
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Turnstile verification failed")


async def verify_turnstile_token(token:str | None, request:Request, expected_action:str) -> None:
    """Verify a one-time Turnstile solution in the request it protects."""
    if(expected_action not in TURNSTILE_ACTIONS):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Turnstile action")

    if(token):
        if(len(token) > 4096):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Turnstile verification required")
        enforce_turnstile_verification_limits(request)
        await _verify_turnstile_response(token, request, expected_action)
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Turnstile verification required")
