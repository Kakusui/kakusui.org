"""Side-effect-free ASGI app for the retired Kakusui and EasyTL hosted services."""

import json

MESSAGE = (
    "Kakusui and EasyTL's hosted services have shut down, effective immediately. "
    "Kaden Bilyeu no longer has time to run them. Translation, account, "
    "payment and other API requests are no longer accepted. "
    "The projects remain open source and available for independent self-hosting."
)
SOURCES = {
    "kakusui_frontend_and_backend": "https://github.com/Kakusui/kakusui.org",
    "easytl_frontend": "https://github.com/Kakusui/EasyTL-Frontend",
    "easytl_library": "https://github.com/ktbilyeu/EasyTL",
}
ALLOWED_ORIGINS = frozenset({
    "https://kakusui.org", "https://kakusui-org.pages.dev",
    "https://easytl.org", "https://easytl-frontend.pages.dev",
})


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            event = await receive()
            if event["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif event["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
    elif scope["type"] == "websocket":
        await send({"type": "websocket.close", "code": 1008,
                    "reason": "Hosted service has shut down."})
    elif scope["type"] == "http":
        # This exact, read-only endpoint only reports process health. It does
        # not grant access to any former service, even with valid credentials.
        healthy = scope["path"] == "/healthz" and scope["method"] in {"GET", "HEAD"}
        payload = {"status": "ok", "service_status": "closed"} if healthy else {
            "error": "service_closed", "detail": MESSAGE, "message": MESSAGE,
            "service_status": "closed", "sources": SOURCES,
        }
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers = [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", str(len(body)).encode("ascii")),
            (b"cache-control", b"no-store"),
            (b"x-content-type-options", b"nosniff"),
            (b"x-frame-options", b"DENY"),
            (b"content-security-policy", b"default-src 'none'; frame-ancestors 'none'"),
            (b"vary", b"Origin"),
        ]
        origin = dict(scope.get("headers", [])).get(b"origin", b"").decode("latin-1")
        if origin in ALLOWED_ORIGINS:
            headers.extend([
                (b"access-control-allow-origin", origin.encode("latin-1")),
                (b"access-control-allow-credentials", b"true"),
            ])
        # Never read bodies or invoke legacy handlers: malformed, oversized,
        # authenticated and unknown requests all receive the same rejection.
        await send({"type": "http.response.start", "status": 200 if healthy else 410,
                    "headers": headers})
        await send({"type": "http.response.body",
                    "body": b"" if scope["method"] == "HEAD" else body})
