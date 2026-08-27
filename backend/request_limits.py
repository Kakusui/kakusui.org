## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

from typing import Any

from starlette.responses import JSONResponse


MAX_REQUEST_BODY_BYTES = 2_621_440  # 2.5 MiB, matching the edge proxy limit.


class RequestBodyTooLarge(BaseException):
    pass


def _contains_body_limit(error: BaseException) -> bool:
    if isinstance(error, RequestBodyTooLarge):
        return True
    nested_errors = getattr(error, "exceptions", ())
    return any(_contains_body_limit(nested_error) for nested_error in nested_errors)


class RequestBodyLimitMiddleware:
    def __init__(self, app: Any, max_body_size: int = MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                declared_size = int(content_length)
            except ValueError:
                declared_size = 0
            if declared_size > self.max_body_size:
                await self._send_rejection(scope, receive, send)
                return

        received_size = 0
        response_started = False

        async def limited_receive():
            nonlocal received_size
            message = await receive()
            if message.get("type") == "http.request":
                received_size += len(message.get("body", b""))
                if received_size > self.max_body_size:
                    raise RequestBodyTooLarge
            return message

        async def tracked_send(message):
            nonlocal response_started
            if message.get("type") == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracked_send)
        except BaseException as error:
            if not _contains_body_limit(error) or response_started:
                raise
            await self._send_rejection(scope, receive, send)

    @staticmethod
    async def _send_rejection(scope: dict, receive: Any, send: Any) -> None:
        response = JSONResponse(
            status_code=413,
            content={"detail": "Request body is too large."},
        )
        await response(scope, receive, send)
