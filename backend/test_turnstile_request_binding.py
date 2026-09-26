from pathlib import Path

import httpx
import pytest
from fastapi import HTTPException
from starlette.requests import Request

import auth.util as auth_util
import routes.turnstile as turnstile
from routes.models import EasyTLRequest, ElucidateRequest, KairyouRequest, SendVerificationEmailRequest


@pytest.fixture(autouse=True)
def isolate_verification(monkeypatch):
    monkeypatch.setattr(turnstile, "enforce_turnstile_verification_limits", lambda request: None)
    monkeypatch.setattr(FakeAsyncClient, "result",
                        {"success": True, "action": "kairyou", "hostname": "kakusui.org"})


def make_request(
    origin: str = "https://kakusui.org",
    client_ip: str = "203.0.113.10",
    server_host: str = "api.kakusui.org",
    include_cf_connecting_ip: bool = True,
    peer_ip: str = "172.18.0.1",
) -> Request:
    headers = [(b"origin", origin.encode())]
    if(include_cf_connecting_ip):
        headers.append((b"cf-connecting-ip", client_ip.encode()))
    return Request({
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "https",
        "path": "/proxy/kairyou",
        "raw_path": b"/proxy/kairyou",
        "query_string": b"",
        "headers": headers,
        "client": (peer_ip, 12345),
        "server": (server_host, 443),
    })


class FakeResponse:
    def __init__(self, result: dict):
        self.result = result

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.result


class FakeAsyncClient:
    result = {"success": True, "action": "kairyou", "hostname": "kakusui.org"}
    init_kwargs: dict = {}
    posted_data: dict = {}

    def __init__(self, **kwargs):
        type(self).init_kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, url: str, data: dict):
        type(self).posted_data = {"url": url, "data": data}
        return FakeResponse(type(self).result)


@pytest.mark.asyncio
async def test_production_verification_is_bounded_and_bound_to_action(monkeypatch):
    monkeypatch.setattr(turnstile, "ENVIRONMENT", "production")
    monkeypatch.setattr(turnstile, "TURNSTILE_SECRET_KEY", "test-secret")
    monkeypatch.setattr(turnstile.httpx, "AsyncClient", FakeAsyncClient)

    await turnstile.verify_turnstile_token("one-time-token", make_request(), "kairyou")

    assert FakeAsyncClient.init_kwargs["follow_redirects"] is False
    assert isinstance(FakeAsyncClient.init_kwargs["timeout"], httpx.Timeout)
    assert FakeAsyncClient.posted_data == {
        "url": turnstile.TURNSTILE_VERIFY_URL,
        "data": {
            "secret": "test-secret",
            "response": "one-time-token",
            "remoteip": "172.18.0.1",
        },
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("result", [
    {"success": False, "action": "kairyou", "hostname": "kakusui.org"},
    {"success": True, "action": "feedback", "hostname": "kakusui.org"},
    {"success": True, "action": "kairyou", "hostname": "attacker.example"},
])
async def test_verification_fails_closed_for_invalid_cloudflare_result(monkeypatch, result):
    monkeypatch.setattr(turnstile, "ENVIRONMENT", "production")
    monkeypatch.setattr(turnstile, "TURNSTILE_SECRET_KEY", "test-secret")
    FakeAsyncClient.result = result
    monkeypatch.setattr(turnstile.httpx, "AsyncClient", FakeAsyncClient)

    with pytest.raises(HTTPException) as exc_info:
        await turnstile.verify_turnstile_token("one-time-token", make_request(), "kairyou")

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_missing_token_fails_before_network_call(monkeypatch):
    monkeypatch.setattr(turnstile, "ENVIRONMENT", "production")
    monkeypatch.setattr(turnstile, "TURNSTILE_SECRET_KEY", "test-secret")

    class UnexpectedClient:
        def __init__(self, **kwargs):
            raise AssertionError("network client must not be created")

    monkeypatch.setattr(turnstile.httpx, "AsyncClient", UnexpectedClient)

    with pytest.raises(HTTPException) as exc_info:
        await turnstile.verify_turnstile_token(None, make_request(), "kairyou")

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_unknown_action_fails_before_network_call(monkeypatch):
    monkeypatch.setattr(turnstile, "ENVIRONMENT", "production")

    class UnexpectedClient:
        def __init__(self, **kwargs):
            raise AssertionError("network client must not be created")

    monkeypatch.setattr(turnstile.httpx, "AsyncClient", UnexpectedClient)

    with pytest.raises(HTTPException) as exc_info:
        await turnstile.verify_turnstile_token("one-time-token", make_request(), "unknown")

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_provider_failure_returns_service_unavailable(monkeypatch):
    monkeypatch.setattr(turnstile, "ENVIRONMENT", "production")
    monkeypatch.setattr(turnstile, "TURNSTILE_SECRET_KEY", "test-secret")

    class FailingClient(FakeAsyncClient):
        async def post(self, url: str, data: dict):
            raise httpx.ConnectTimeout("timed out")

    monkeypatch.setattr(turnstile.httpx, "AsyncClient", FailingClient)

    with pytest.raises(HTTPException) as exc_info:
        await turnstile.verify_turnstile_token("one-time-token", make_request(), "kairyou")

    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_development_mode_has_explicit_offline_bypass(monkeypatch):
    monkeypatch.setattr(turnstile, "ENVIRONMENT", "development")
    monkeypatch.setattr(turnstile, "TURNSTILE_SECRET_KEY", None)

    class UnexpectedClient:
        def __init__(self, **kwargs):
            raise AssertionError("development bypass must not call Cloudflare")

    monkeypatch.setattr(turnstile.httpx, "AsyncClient", UnexpectedClient)
    await turnstile.verify_turnstile_token(
        "local-test-token",
        make_request(
            "http://localhost:5173",
            server_host="api.localhost",
            include_cf_connecting_ip=False,
        ),
        "kairyou",
    )

    with pytest.raises(HTTPException) as exc_info:
        await turnstile.verify_turnstile_token(
            "local-test-token",
            make_request("https://kakusui.org", server_host="api.kakusui.org"),
            "kairyou",
        )
    assert exc_info.value.status_code == 503

    with pytest.raises(HTTPException) as exc_info:
        await turnstile.verify_turnstile_token(
            "local-test-token",
            make_request(
                "http://localhost:5173",
                server_host="api.localhost",
                include_cf_connecting_ip=False,
                peer_ip="8.8.8.8",
            ),
            "kairyou",
        )
    assert exc_info.value.status_code == 503


@pytest.mark.asyncio
async def test_origin_allowlist_is_exact_not_suffix_based(monkeypatch):
    monkeypatch.setattr(auth_util, "ENVIRONMENT", "production")
    await auth_util.check_internal_request(make_request("https://kakusui.org"))
    for origin in ("https://preview.kakusui-org.pages.dev", "https://kakusui.org.attacker.example", "https://evilhttps://kakusui.org"):
        with pytest.raises(HTTPException) as exc_info:
            await auth_util.check_internal_request(make_request(origin))
        assert exc_info.value.status_code == 403


def test_turnstile_token_is_explicitly_removed_from_forwarded_models():
    models = [
        KairyouRequest(textToPreprocess="text", replacementsJson="{}", turnstile_token="secret"),
        ElucidateRequest(
            textToEvaluate="text",
            evaluationInstructions="instructions",
            llmType="openai",
            userAPIKey="key",
            model="model",
            turnstile_token="secret",
        ),
        EasyTLRequest(
            textToTranslate="text",
            translationInstructions="instructions",
            llmType="openai",
            userAPIKey="key",
            model="model",
            using_credits=False,
            turnstile_token="secret",
        ),
        SendVerificationEmailRequest(
            email="person@example.com",
            clientID="client",
            turnstile_token="secret",
        ),
    ]

    for model in models:
        assert "turnstile_token" not in model.model_dump(exclude={"turnstile_token"})


def test_sensitive_call_sites_require_direct_verification_and_frontend_no_longer_preverifies():
    root = Path(__file__).resolve().parents[1]
    backend_expectations = {
        "backend/routes/kairyou.py": ['verify_turnstile_token(request_data.turnstile_token, request, "kairyou")'],
        "backend/routes/elucidate.py": ['verify_turnstile_token(request_data.turnstile_token, request, "elucidate")'],
        "backend/routes/easytl.py": [
            'verify_turnstile_token(request_data.turnstile_token, request, "easytl")',
            'verify_turnstile_token(request_data.turnstile_token, request, "easytl_stream")',
            'verify_turnstile_token(request_data.turnstile_token, request, "easytl_detect")',
        ],
        "backend/routes/email.py": ['verify_turnstile_token(feedback.turnstile_token, request, "feedback")'],
        "backend/routes/auth.py": ['verify_turnstile_token(request_data.turnstile_token, request, "verification_email")'],
    }
    for relative_path, expected_calls in backend_expectations.items():
        source = (root / relative_path).read_text()
        for expected_call in expected_calls:
            assert expected_call in source

    frontend_files = [
        root / "frontend/src/pages/KairyouPage.tsx",
        root / "frontend/src/pages/ElucidatePage.tsx",
        root / "frontend/src/pages/EasyTLPage.tsx",
    ]
    for frontend_file in frontend_files:
        source = frontend_file.read_text()
        assert "/auth/verify-turnstile" not in source
        assert "turnstile_token" in source
        assert "setTurnstileToken(null)" in source

    turnstile_source = (root / "backend/routes/turnstile.py").read_text()
    assert '@router.post("/auth/verify-turnstile")' not in turnstile_source


def test_all_supported_production_hostnames_are_exactly_allowlisted(monkeypatch):
    monkeypatch.setattr(turnstile, "ENVIRONMENT", "production")
    for hostname in turnstile.TURNSTILE_HOSTNAMES:
        assert turnstile._is_allowed_hostname(hostname)
    assert not turnstile._is_allowed_hostname("preview.kakusui-org.pages.dev")
    assert not turnstile._is_allowed_hostname("kakusui.org.attacker.example")
    assert not turnstile._is_allowed_hostname("evil-kakusui-org.pages.dev")
