import asyncio
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.credit_accounting import CreditReservationStatus, reserve_credits
from db.models import EndpointStats, User
from routes import easytl as easytl_route
from routes.models import EasyTLRequest, LanguageDetectionRequest, TokenCostRequest


class FakeEasyTL:
    credentials = None
    credential_tests = 0
    provider_calls = 0
    fail_credential_setup = False
    fail_translation = False
    fail_stream_start = False
    translation_result = "translated"
    stream_chunks = ["translated"]
    last_translation_kwargs = None
    last_stream_kwargs = None
    credential_observations = []
    observe_credentials_across_await = False

    @classmethod
    def reset(cls):
        cls.credentials = None
        cls.credential_tests = 0
        cls.provider_calls = 0
        cls.fail_credential_setup = False
        cls.fail_translation = False
        cls.fail_stream_start = False
        cls.translation_result = "translated"
        cls.stream_chunks = ["translated"]
        cls.last_translation_kwargs = None
        cls.last_stream_kwargs = None
        cls.credential_observations = []
        cls.observe_credentials_across_await = False

    @classmethod
    def set_credentials(cls, api_type, credentials):
        if cls.fail_credential_setup:
            raise ValueError("local credential configuration failed")
        cls.credentials = (api_type, credentials)

    @classmethod
    def test_credentials(cls, api_type):
        cls.credential_tests += 1
        cls.provider_calls += 1

    @classmethod
    async def translate_async(cls, **kwargs):
        cls.last_translation_kwargs = kwargs
        cls.provider_calls += 1
        initial_credentials = cls.credentials
        if(cls.observe_credentials_across_await):
            await asyncio.sleep(0)
        cls.credential_observations.append((initial_credentials, cls.credentials))
        if cls.fail_translation:
            raise RuntimeError("provider request failed")
        return cls.translation_result

    @classmethod
    async def openai_translate_async(cls, **kwargs):
        cls.last_stream_kwargs = kwargs
        cls.provider_calls += 1
        if cls.fail_stream_start:
            raise RuntimeError("provider stream failed to start")

        async def stream():
            for text in cls.stream_chunks:
                delta = SimpleNamespace(content=text)
                choice = SimpleNamespace(delta=delta)
                yield SimpleNamespace(choices=[choice])

        return stream()


class EasyTLCreditAccountingTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        FakeEasyTL.reset()
        self.tempdir = tempfile.TemporaryDirectory()
        database_path = Path(self.tempdir.name) / "credits.db"
        self.engine = create_engine(
            f"sqlite:///{database_path}",
            connect_args={"check_same_thread": False},
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        overrides = {
            "SessionLocal": self.Session,
            "EasyTL": FakeEasyTL,
            "V1_EASYTL_ROOT_KEY": "root-key",
            "V1_EASYTL_PUBLIC_API_KEY": "public-key",
            "get_admin_api_key": AsyncMock(return_value="server-key"),
            "check_internal_request": AsyncMock(),
            "verify_turnstile_token": AsyncMock(),
            "get_backend_url": AsyncMock(return_value="http://backend"),
        }
        for name, value in overrides.items():
            dependency = patch.object(easytl_route, name, value)
            dependency.start()
            self.addCleanup(dependency.stop)
        self.request = SimpleNamespace(headers={"X-API-Key": "root-key"})

        with self.Session() as db:
            db.add(EndpointStats(endpoint="EasyTL", count=0))
            db.commit()

    def tearDown(self):
        self.engine.dispose()
        self.tempdir.cleanup()

    def add_user(self, email="user@example.com", credits=100):
        with self.Session() as db:
            db.add(User(email=email, credits=credits))
            db.commit()

    def balance(self, email="user@example.com"):
        with self.Session() as db:
            return db.execute(select(User.credits).where(User.email == email)).scalar_one()

    @staticmethod
    def response_json(response):
        return json.loads(response.body)

    @staticmethod
    async def consume_stream(response):
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        if response.background is not None:
            await response.background()
        return chunks

    async def test_invalid_model_is_rejected_before_any_provider_call(self):
        request_data = EasyTLRequest(
            textToTranslate="hello",
            translationInstructions="",
            llmType="openai",
            userAPIKey="user-key",
            model="not-a-model",
            using_credits=False,
        )

        with self.Session() as db:
            response = await easytl_route.easytl(
                request_data,
                self.request,
                is_admin=False,
                db=db,
                current_user="",
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(FakeEasyTL.provider_calls, 0)
        self.assertEqual(FakeEasyTL.credential_tests, 0)
        self.assertIsNone(FakeEasyTL.credentials)

    async def test_proxy_turnstile_rejection_prevents_internal_forwarding(self):
        request_data = EasyTLRequest(
            textToTranslate="hello",
            translationInstructions="translate",
            llmType="openai",
            userAPIKey="user-key",
            model="gpt-4o-mini",
            using_credits=False,
            turnstile_token="invalid-token",
        )
        verification_calls = []

        async def reject_token(token, request, action):
            verification_calls.append((token, action))
            raise HTTPException(status_code=403, detail="rejected")

        class UnexpectedClient:
            def __init__(self, **kwargs):
                raise AssertionError("rejected requests must not be forwarded")

        original_verifier = easytl_route.verify_turnstile_token
        original_client = easytl_route.httpx.AsyncClient
        easytl_route.verify_turnstile_token = reject_token
        easytl_route.httpx.AsyncClient = UnexpectedClient
        try:
            with self.assertRaises(HTTPException):
                await easytl_route.proxy_easytl(request_data, self.request)
        finally:
            easytl_route.verify_turnstile_token = original_verifier
            easytl_route.httpx.AsyncClient = original_client

        self.assertEqual(verification_calls, [("invalid-token", "easytl")])

    async def test_concurrent_byok_requests_keep_request_scoped_credentials(self):
        FakeEasyTL.observe_credentials_across_await = True

        async def submit(api_key):
            request_data = EasyTLRequest(
                textToTranslate="hello",
                translationInstructions="translate",
                llmType="openai",
                userAPIKey=api_key,
                model="gpt-4o-mini",
                using_credits=False,
            )
            with self.Session() as db:
                return await easytl_route.easytl(
                    request_data,
                    self.request,
                    is_admin=False,
                    db=db,
                    current_user="",
                )

        responses = await asyncio.gather(submit("user-key-a"), submit("user-key-b"))

        self.assertEqual([response.status_code for response in responses], [200, 200])
        observed_keys = set()
        for initial_credentials, final_credentials in FakeEasyTL.credential_observations:
            self.assertEqual(initial_credentials, final_credentials)
            observed_keys.add(initial_credentials[1])
        self.assertEqual(observed_keys, {"user-key-a", "user-key-b"})

    async def test_proxy_strips_turnstile_token_before_internal_forwarding(self):
        request_data = EasyTLRequest(
            textToTranslate="hello",
            translationInstructions="translate",
            llmType="openai",
            userAPIKey="user-key",
            model="gpt-4o-mini",
            using_credits=False,
            turnstile_token="one-time-token",
        )
        forwarded = {}

        async def accept_token(token, request, action):
            return None

        class FakeResponse:
            status_code = 200

            @staticmethod
            def json():
                return {"translatedText": "translated"}

        class FakeClient:
            def __init__(self, **kwargs):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, traceback):
                return False

            async def post(self, url, json, headers):
                forwarded.update({"url": url, "json": json, "headers": headers})
                return FakeResponse()

        original_verifier = easytl_route.verify_turnstile_token
        original_client = easytl_route.httpx.AsyncClient
        easytl_route.verify_turnstile_token = accept_token
        easytl_route.httpx.AsyncClient = FakeClient
        try:
            response = await easytl_route.proxy_easytl(request_data, self.request)
        finally:
            easytl_route.verify_turnstile_token = original_verifier
            easytl_route.httpx.AsyncClient = original_client

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("turnstile_token", forwarded["json"])

    async def test_whitespace_only_credit_request_never_reaches_provider(self):
        self.add_user(credits=0)
        request_data = EasyTLRequest(
            textToTranslate=" \n\t",
            translationInstructions="",
            llmType="openai",
            userAPIKey="",
            model="gpt-4",
            using_credits=True,
        )

        with self.Session() as db:
            response = await easytl_route.easytl(
                request_data,
                self.request,
                is_admin=True,
                db=db,
                current_user="user@example.com",
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(FakeEasyTL.provider_calls, 0)
        self.assertIsNone(FakeEasyTL.credentials)
        self.assertEqual(self.balance(), 0)

    async def test_zero_balance_never_reaches_server_funded_provider(self):
        self.add_user(credits=0)
        request_data = EasyTLRequest(
            textToTranslate="abcdefghij",
            translationInstructions="",
            llmType="openai",
            userAPIKey="",
            model="gpt-4",
            using_credits=True,
        )

        with self.Session() as db:
            response = await easytl_route.easytl(
                request_data,
                self.request,
                is_admin=True,
                db=db,
                current_user="user@example.com",
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(FakeEasyTL.provider_calls, 0)
        self.assertEqual(FakeEasyTL.credential_tests, 0)
        self.assertEqual(self.balance(), 0)

    async def test_user_supplied_key_mode_is_preserved(self):
        request_data = EasyTLRequest(
            textToTranslate="hello",
            translationInstructions="",
            llmType="openai",
            userAPIKey="user-key",
            model="gpt-4o-mini",
            using_credits=False,
        )

        with self.Session() as db:
            response = await easytl_route.easytl(
                request_data,
                self.request,
                is_admin=False,
                db=db,
                current_user="",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(FakeEasyTL.credentials, ("openai", "user-key"))
        self.assertEqual(FakeEasyTL.credential_tests, 1)
        self.assertEqual(FakeEasyTL.provider_calls, 2)
        self.assertEqual(self.response_json(response)["credits"], -1)
        self.assertEqual(FakeEasyTL.last_translation_kwargs["max_tokens"], 64)

    async def test_detect_language_reserves_before_provider_call(self):
        starting_credits = 1000
        self.add_user(credits=starting_credits)
        FakeEasyTL.translation_result = "Japanese"
        request_data = LanguageDetectionRequest(
            text="abcdefghij",
            llmType="openai",
            userAPIKey="",
            model="gpt-4",
            using_credits=True,
        )

        with self.Session() as db:
            response = await easytl_route.detect_language(
                request_data,
                self.request,
                is_admin=True,
                db=db,
                current_user="user@example.com",
            )

        provider_text, provider_instructions = easytl_route._prepare_language_detection_payload(
            request_data.text
        )
        expected_cost = easytl_route._calculate_credit_cost(
            provider_text, provider_instructions, request_data.model
        )
        body = self.response_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["detectedLanguage"], "Japanese")
        self.assertAlmostEqual(body["cost"], expected_cost)
        self.assertAlmostEqual(body["credits"], starting_credits - expected_cost)
        self.assertAlmostEqual(self.balance(), starting_credits - expected_cost)
        self.assertEqual(FakeEasyTL.provider_calls, 1)
        self.assertEqual(FakeEasyTL.credential_tests, 0)
        self.assertEqual(FakeEasyTL.last_translation_kwargs["text"], provider_text)
        self.assertEqual(
            FakeEasyTL.last_translation_kwargs["translation_instructions"],
            provider_instructions,
        )
        self.assertEqual(FakeEasyTL.last_translation_kwargs["max_tokens"], 16)

    async def test_unsophisticated_model_estimate_matches_provider_bound_charge(self):
        starting_credits = 1000
        self.add_user(credits=starting_credits)
        request_data = EasyTLRequest(
            textToTranslate="x",
            translationInstructions="translate faithfully",
            llmType="anthropic",
            userAPIKey="",
            model="claude-3-opus-20240229",
            using_credits=True,
        )

        estimate_response = await easytl_route.calculate_token_cost(TokenCostRequest(
            text_to_translate=request_data.textToTranslate,
            translation_instructions=request_data.translationInstructions,
            model=request_data.model,
        ))
        with self.Session() as db:
            response = await easytl_route.easytl(
                request_data,
                self.request,
                is_admin=True,
                db=db,
                current_user="user@example.com",
            )

        expected_text, expected_instructions = easytl_route._prepare_translation_payload(
            request_data.textToTranslate,
            request_data.translationInstructions,
            request_data.model,
        )
        body = self.response_json(response)
        estimate = self.response_json(estimate_response)["cost"]
        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(body["cost"], estimate)
        self.assertAlmostEqual(self.balance(), starting_credits - estimate)
        self.assertEqual(FakeEasyTL.last_translation_kwargs["text"], expected_text)
        self.assertEqual(
            FakeEasyTL.last_translation_kwargs["translation_instructions"],
            expected_instructions,
        )
        self.assertEqual(FakeEasyTL.last_translation_kwargs["max_output_tokens"], 64)

    async def test_stream_abandoned_before_provider_invocation_is_refunded(self):
        self.add_user(credits=100)
        request_data = EasyTLRequest(
            textToTranslate="abcdefghij",
            translationInstructions="",
            llmType="openai",
            userAPIKey="",
            model="gpt-4",
            using_credits=True,
        )

        with self.Session() as db:
            response = await easytl_route.easytl_stream(
                request_data,
                self.request,
                is_admin=True,
                db=db,
                current_user="user@example.com",
            )

        self.assertEqual(self.balance(), 93)
        await response.background()
        await response.background()
        self.assertEqual(self.balance(), 100)
        self.assertEqual(FakeEasyTL.provider_calls, 0)

    async def test_stream_local_setup_failure_is_refunded_before_provider_call(self):
        self.add_user(credits=100)
        FakeEasyTL.fail_credential_setup = True
        request_data = EasyTLRequest(
            textToTranslate="abcdefghij",
            translationInstructions="",
            llmType="openai",
            userAPIKey="",
            model="gpt-4",
            using_credits=True,
        )

        with self.Session() as db:
            response = await easytl_route.easytl_stream(
                request_data,
                self.request,
                is_admin=True,
                db=db,
                current_user="user@example.com",
            )
        chunks = await self.consume_stream(response)

        self.assertTrue(any("error" in chunk for chunk in chunks))
        self.assertEqual(self.balance(), 100)
        self.assertEqual(FakeEasyTL.provider_calls, 0)

    async def test_stream_cancellation_after_provider_start_keeps_charge(self):
        self.add_user(credits=100)
        FakeEasyTL.stream_chunks = ["first", "second"]
        request_data = EasyTLRequest(
            textToTranslate="abcdefghij",
            translationInstructions="",
            llmType="openai",
            userAPIKey="",
            model="gpt-4",
            using_credits=True,
        )

        with self.Session() as db:
            response = await easytl_route.easytl_stream(
                request_data,
                self.request,
                is_admin=True,
                db=db,
                current_user="user@example.com",
            )

        first_chunk = await response.body_iterator.__anext__()
        self.assertIn("first", first_chunk)
        await response.body_iterator.aclose()
        await response.background()

        self.assertEqual(self.balance(), 93)
        self.assertEqual(FakeEasyTL.provider_calls, 1)
        self.assertEqual(FakeEasyTL.last_stream_kwargs["max_tokens"], 64)

    async def test_provider_failure_after_billing_boundary_keeps_charge(self):
        self.add_user(credits=100)
        FakeEasyTL.fail_stream_start = True
        request_data = EasyTLRequest(
            textToTranslate="abcdefghij",
            translationInstructions="",
            llmType="openai",
            userAPIKey="",
            model="gpt-4",
            using_credits=True,
        )

        with self.Session() as db:
            response = await easytl_route.easytl_stream(
                request_data,
                self.request,
                is_admin=True,
                db=db,
                current_user="user@example.com",
            )
        await self.consume_stream(response)

        self.assertEqual(self.balance(), 93)
        self.assertEqual(FakeEasyTL.provider_calls, 1)

    async def test_nonstream_provider_failure_keeps_reserved_charge(self):
        self.add_user(credits=100)
        FakeEasyTL.fail_translation = True
        request_data = EasyTLRequest(
            textToTranslate="abcdefghij",
            translationInstructions="",
            llmType="openai",
            userAPIKey="",
            model="gpt-4",
            using_credits=True,
        )

        with self.Session() as db:
            response = await easytl_route.easytl(
                request_data,
                self.request,
                is_admin=True,
                db=db,
                current_user="user@example.com",
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.balance(), 93)
        self.assertEqual(FakeEasyTL.provider_calls, 1)


class AtomicReservationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        database_path = Path(self.tempdir.name) / "concurrency.db"
        self.engine = create_engine(
            f"sqlite:///{database_path}",
            connect_args={"check_same_thread": False},
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        with self.Session() as db:
            db.add(User(email="race@example.com", credits=10))
            db.commit()

    def tearDown(self):
        self.engine.dispose()
        self.tempdir.cleanup()

    def test_concurrent_reservations_cannot_overdraw_balance(self):
        def reserve():
            with self.Session() as db:
                return reserve_credits(db, "race@example.com", 7).status

        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(lambda _: reserve(), range(2)))

        self.assertEqual(statuses.count(CreditReservationStatus.RESERVED), 1)
        self.assertEqual(statuses.count(CreditReservationStatus.INSUFFICIENT_CREDITS), 1)
        with self.Session() as db:
            balance = db.execute(
                select(User.credits).where(User.email == "race@example.com")
            ).scalar_one()
        self.assertEqual(balance, 3)
        self.assertGreaterEqual(balance, 0)


if __name__ == "__main__":
    unittest.main()
