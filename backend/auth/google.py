## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

import threading
import time
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2 import id_token


GOOGLE_CERT_CACHE_SECONDS = 300


class _CachedGoogleRequest:
    """Cache Google's public signing certificates and prevent fetch stampedes."""

    def __init__(self) -> None:
        self._transport = Request()
        self._lock = threading.Lock()
        self._cached_responses: dict[str, tuple[float, Any]] = {}

    def __call__(
        self,
        url: str,
        method: str = "GET",
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: int = 10,
        **kwargs: Any,
    ) -> Any:
        if method.upper() != "GET" or body is not None:
            return self._transport(url, method, body, headers, timeout, **kwargs)

        with self._lock:
            now = time.monotonic()
            cached = self._cached_responses.get(url)
            if cached is not None and cached[0] > now:
                return cached[1]

            response = self._transport(url, method, body, headers, timeout, **kwargs)
            if response.status == 200:
                self._cached_responses[url] = (
                    now + GOOGLE_CERT_CACHE_SECONDS,
                    response,
                )
            return response


_google_request = _CachedGoogleRequest()


def verify_google_id_token(token: str, audience: str) -> dict[str, Any]:
    return id_token.verify_oauth2_token(token, _google_request, audience)
