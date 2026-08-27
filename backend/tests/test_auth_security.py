import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi import HTTPException
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from auth import client, func as auth_func, util as auth_util
from auth import throttle, verification
from db.base import Base
from db.models import User
from routes import auth as auth_routes
from routes import turnstile


class AuthSecurityTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.engine = create_engine(
            f"sqlite:///{self.tempdir.name}/auth.db",
            connect_args={"check_same_thread": False},
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

        self.original_verification_session = verification.SessionLocal
        self.original_throttle_session = throttle.SessionLocal
        self.original_verification_secret = verification.ACCESS_TOKEN_SECRET
        self.original_access_secret = auth_func.ACCESS_TOKEN_SECRET
        self.original_refresh_secret = auth_func.REFRESH_TOKEN_SECRET

        verification.SessionLocal = self.Session
        throttle.SessionLocal = self.Session
        verification.ACCESS_TOKEN_SECRET = "verification-test-secret-at-least-32-bytes"
        auth_func.ACCESS_TOKEN_SECRET = "access-test-secret-at-least-32-bytes"
        auth_func.REFRESH_TOKEN_SECRET = "refresh-test-secret-at-least-32-bytes"

    def tearDown(self):
        verification.SessionLocal = self.original_verification_session
        throttle.SessionLocal = self.original_throttle_session
        verification.ACCESS_TOKEN_SECRET = self.original_verification_secret
        auth_func.ACCESS_TOKEN_SECRET = self.original_access_secret
        auth_func.REFRESH_TOKEN_SECRET = self.original_refresh_secret
        self.engine.dispose()
        self.tempdir.cleanup()

    def test_reissuing_code_does_not_reset_failed_attempts(self):
        email = "User@Example.test"
        verification.save_verification_data(email, "123456")
        self.assertFalse(verification.verify_verification_code(email, "000000"))
        self.assertFalse(verification.verify_verification_code(email, "000001"))

        verification.save_verification_data("User@example.test", "654321")
        self.assertFalse(verification.verify_verification_code(email, "000002"))

        with self.assertRaises(verification.VerificationAttemptsExceeded):
            verification.save_verification_data(email, "111111")

    def test_concurrent_guesses_cannot_exceed_attempt_limit(self):
        email = "race@example.test"
        verification.save_verification_data(email, "999999")

        def guess(number):
            try:
                return verification.verify_verification_code(email, f"{number:06d}")
            except verification.VerificationAttemptsExceeded:
                return "limited"

        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(guess, range(6)))

        self.assertEqual(results.count(False), 3)
        self.assertEqual(results.count("limited"), 3)

    def test_rate_limit_increment_is_atomic(self):
        scope = f"test-{uuid4().hex}"

        def consume(_):
            try:
                throttle.consume_rate_limit(
                    scope,
                    "same-source",
                    limit=3,
                    window_seconds=60,
                )
                return "accepted"
            except HTTPException as error:
                return error.status_code

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(consume, range(5)))

        self.assertEqual(results.count("accepted"), 3)
        self.assertEqual(results.count(429), 2)

    def test_client_rate_limit_identifier_ignores_spoofable_cf_header(self):
        def request_with_cf_header(value):
            return Request(
                {
                    "type": "http",
                    "method": "POST",
                    "path": "/auth/login",
                    "headers": [(b"cf-connecting-ip", value.encode())],
                    "client": ("198.51.100.7", 12345),
                }
            )

        first = client.get_request_client_identifier(request_with_cf_header("203.0.113.1"))
        second = client.get_request_client_identifier(request_with_cf_header("203.0.113.2"))
        self.assertEqual(first, "198.51.100.7")
        self.assertEqual(second, first)

    def test_fly_and_cloudflare_client_headers_are_validated(self):
        def make_request(fly_client, cloudflare_client):
            return Request(
                {
                    "type": "http",
                    "method": "POST",
                    "path": "/auth/login",
                    "headers": [
                        (b"fly-client-ip", fly_client.encode()),
                        (b"cf-connecting-ip", cloudflare_client.encode()),
                    ],
                    "client": ("fdaa::1", 12345),
                }
            )

        with patch.object(client, "IS_FLY_RUNTIME", True):
            direct = client.get_request_client_identifier(
                make_request("198.51.100.7", "203.0.113.99")
            )
            cloudflare = client.get_request_client_identifier(
                make_request("104.16.1.1", "203.0.113.99")
            )
        self.assertEqual(direct, "198.51.100.7")
        self.assertEqual(cloudflare, "203.0.113.99")

    def test_ipv6_rate_limits_are_grouped_by_64_prefix(self):
        def make_request(address):
            return Request(
                {
                    "type": "http",
                    "method": "POST",
                    "path": "/auth/login",
                    "headers": [],
                    "client": (address, 12345),
                }
            )

        first = client.get_request_client_identifier(make_request("2001:db8:1:2::1"))
        same_prefix = client.get_request_client_identifier(
            make_request("2001:db8:1:2:ffff::2")
        )
        different_prefix = client.get_request_client_identifier(
            make_request("2001:db8:1:3::1")
        )
        self.assertEqual(first, "2001:db8:1:2::/64")
        self.assertEqual(first, same_prefix)
        self.assertNotEqual(first, different_prefix)

    def test_source_limit_fails_before_global_limit(self):
        request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/auth/login",
                "headers": [],
                "client": ("198.51.100.7", 12345),
            }
        )
        calls = []

        def fail_source(scope, *_args, **_kwargs):
            calls.append(scope)
            raise HTTPException(status_code=429)

        with patch.object(throttle, "consume_rate_limit", side_effect=fail_source):
            with self.assertRaises(HTTPException):
                throttle.enforce_otp_verify_limits(request, "user@example.com")
        self.assertEqual(calls, ["otp-verify-source"])

    def test_turnstile_source_limit_fails_before_global_limit(self):
        request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/proxy/kairyou",
                "headers": [],
                "client": ("198.51.100.7", 12345),
            }
        )
        calls = []

        def fail_source(scope, *_args, **_kwargs):
            calls.append(scope)
            raise HTTPException(status_code=429)

        with patch.object(throttle, "consume_rate_limit", side_effect=fail_source):
            with self.assertRaises(HTTPException):
                throttle.enforce_turnstile_verification_limits(request)
        self.assertEqual(calls, ["turnstile-source"])

    def test_google_login_source_limit_fails_before_global_limit(self):
        request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/auth/google-login",
                "headers": [],
                "client": ("198.51.100.7", 12345),
            }
        )
        calls = []

        def fail_source(scope, *_args, **_kwargs):
            calls.append(scope)
            raise HTTPException(status_code=429)

        with patch.object(throttle, "consume_rate_limit", side_effect=fail_source):
            with self.assertRaises(HTTPException):
                throttle.enforce_google_login_limits(request)
        self.assertEqual(calls, ["google-login-source"])

    def test_cookie_auth_rejects_pages_preview_origins(self):
        def make_request(origin):
            return Request(
                {
                    "type": "http",
                    "method": "POST",
                    "path": "/auth/refresh-access-token",
                    "headers": [(b"origin", origin.encode())],
                    "client": ("198.51.100.7", 12345),
                }
            )

        asyncio.run(auth_util.check_internal_request(make_request("https://kakusui.org")))
        with self.assertRaises(HTTPException):
            asyncio.run(
                auth_util.check_internal_request(
                    make_request("https://attacker.kakusui-org.pages.dev")
                )
            )

    def test_turnstile_rejects_pages_preview_hostname(self):
        self.assertTrue(turnstile._is_allowed_hostname("kakusui.org"))
        self.assertFalse(
            turnstile._is_allowed_hostname("attacker.kakusui-org.pages.dev")
        )

    def test_email_identity_preserves_local_part_case(self):
        with self.Session() as db:
            db.add_all(
                [
                    User(email="User@example.com"),
                    User(email="user@example.com"),
                ]
            )
            db.commit()
            upper_local = auth_routes._find_user_by_email(db, "User@EXAMPLE.COM")
            lower_local = auth_routes._find_user_by_email(db, "user@example.com")
            self.assertEqual(upper_local.email, "User@example.com")
            self.assertEqual(lower_local.email, "user@example.com")

    def test_typed_tokens_are_not_interchangeable(self):
        async def exercise():
            access = await auth_func.create_access_token(
                {"sub": "user@example.test"}, timedelta(minutes=5)
            )
            refresh = await auth_func.create_refresh_token(
                {"sub": "user@example.test"}, timedelta(minutes=5)
            )

            self.assertEqual((await auth_func.func_verify_token(access)).email, "user@example.test")
            self.assertEqual(
                (await auth_func.func_verify_token(refresh, token_type="refresh")).email,
                "user@example.test",
            )
            with self.assertRaises(HTTPException):
                await auth_func.func_verify_token(access, token_type="refresh")
            with self.assertRaises(HTTPException):
                await auth_func.func_verify_token(refresh, token_type="access")

        asyncio.run(exercise())

    def test_default_access_and_refresh_lifetimes_are_separate(self):
        async def exercise():
            access = await auth_func.create_access_token(
                {"sub": "user@example.test"},
                None,
            )
            refresh = await auth_func.create_refresh_token(
                {"sub": "user@example.test"},
                None,
            )
            access_payload = jwt.decode(
                access,
                auth_func.ACCESS_TOKEN_SECRET,
                algorithms=[auth_func.TOKEN_ALGORITHM],
            )
            refresh_payload = jwt.decode(
                refresh,
                auth_func.REFRESH_TOKEN_SECRET,
                algorithms=[auth_func.TOKEN_ALGORITHM],
            )
            lifetime_gap = refresh_payload["exp"] - access_payload["exp"]
            self.assertGreater(lifetime_gap, 29 * 24 * 60 * 60)

        asyncio.run(exercise())

    def test_legacy_refresh_requires_a_distinct_signing_secret(self):
        expiration = datetime.now(timezone.utc) + timedelta(minutes=5)
        legacy_refresh = jwt.encode(
            {"sub": "user@example.test", "exp": expiration},
            auth_func.REFRESH_TOKEN_SECRET,
            algorithm=auth_func.TOKEN_ALGORITHM,
        )

        async def accept_separated_legacy_token():
            token_data = await auth_func.func_verify_token(
                legacy_refresh,
                token_type="refresh",
            )
            self.assertEqual(token_data.email, "user@example.test")

        asyncio.run(accept_separated_legacy_token())

        shared_secret = "shared-test-secret-at-least-32-bytes"
        auth_func.ACCESS_TOKEN_SECRET = shared_secret
        auth_func.REFRESH_TOKEN_SECRET = shared_secret
        ambiguous_legacy_token = jwt.encode(
            {"sub": "user@example.test", "exp": expiration},
            shared_secret,
            algorithm=auth_func.TOKEN_ALGORITHM,
        )

        async def reject_ambiguous_legacy_token():
            with self.assertRaises(HTTPException):
                await auth_func.func_verify_token(
                    ambiguous_legacy_token,
                    token_type="refresh",
                )
            with self.assertRaises(HTTPException):
                await auth_func.func_verify_token(ambiguous_legacy_token)

        asyncio.run(reject_ambiguous_legacy_token())


if __name__ == "__main__":
    unittest.main()
