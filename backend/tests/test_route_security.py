import unittest

from fastapi import HTTPException
from starlette.requests import Request

from routes import db as db_routes
from routes import auth as auth_routes
from routes.models import RegisterForEmailAlert
from request_limits import RequestBodyLimitMiddleware


class DatabaseRestoreSecurityTests(unittest.IsolatedAsyncioTestCase):
    async def test_online_restore_is_disabled_without_reading_request_body(self):
        body_was_read = False

        async def receive():
            nonlocal body_was_read
            body_was_read = True
            raise AssertionError("disabled restore must not read multipart data")

        request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/admin/db/replace-database",
                "headers": [(b"origin", b"https://kakusui.org")],
                "client": ("198.51.100.7", 12345),
            },
            receive,
        )

        with self.assertRaises(HTTPException) as raised:
            await db_routes.upload_backup(request, is_admin=True)

        self.assertEqual(raised.exception.status_code, 503)
        self.assertFalse(body_was_read)


class AuthRouteSecurityTests(unittest.IsolatedAsyncioTestCase):
    def make_request(self, path):
        return Request(
            {
                "type": "http",
                "method": "POST",
                "path": path,
                "headers": [(b"origin", b"https://kakusui.org")],
                "client": ("198.51.100.7", 12345),
            }
        )

    async def test_registration_check_is_uniform_and_query_free(self):
        response = await auth_routes.check_email_registration(
            RegisterForEmailAlert(email="user@example.com"),
            self.make_request("/auth/check-email-registration"),
        )
        self.assertEqual(response.body, b'{"accepted":true}')

    async def test_logout_expires_http_only_refresh_cookie(self):
        response = await auth_routes.logout(self.make_request("/auth/logout"))
        cookie = response.headers["set-cookie"].lower()
        self.assertIn("refresh_token=", cookie)
        self.assertIn("max-age=0", cookie)
        self.assertIn("httponly", cookie)
        self.assertIn("samesite=none", cookie)
        self.assertIn("secure", cookie)


class RequestBodyLimitTests(unittest.IsolatedAsyncioTestCase):
    async def test_chunked_body_is_rejected_before_application_processing(self):
        app_read_bytes = 0

        async def app(_scope, receive, send):
            nonlocal app_read_bytes
            while True:
                message = await receive()
                app_read_bytes += len(message.get("body", b""))
                if not message.get("more_body", False):
                    break
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})

        messages = iter(
            [
                {"type": "http.request", "body": b"a" * 6, "more_body": True},
                {"type": "http.request", "body": b"b" * 6, "more_body": False},
            ]
        )
        sent = []

        async def receive():
            return next(messages)

        async def send(message):
            sent.append(message)

        middleware = RequestBodyLimitMiddleware(app, max_body_size=10)
        await middleware(
            {
                "type": "http",
                "method": "POST",
                "path": "/test",
                "headers": [],
            },
            receive,
            send,
        )

        self.assertEqual(sent[0]["status"], 413)
        self.assertEqual(app_read_bytes, 6)


if __name__ == "__main__":
    unittest.main()
