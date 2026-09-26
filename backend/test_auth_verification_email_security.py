import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from routes import auth as auth_route
from routes.models import SendVerificationEmailRequest


@pytest.fixture
def email_flow(monkeypatch):
    dependencies = {
        "check_internal_request": AsyncMock(),
        "enforce_otp_issue_source_limit": Mock(),
        "verify_turnstile_token": AsyncMock(),
        "enforce_otp_issue_limits_after_verification": Mock(),
        "generate_verification_code": AsyncMock(return_value="123456"),
        "save_verification_data": AsyncMock(),
        "send_verification_email": AsyncMock(),
    }
    for name, dependency in dependencies.items():
        monkeypatch.setattr(auth_route, name, dependency)
    return SimpleNamespace(**dependencies)


def make_request():
    return Request({
        "type": "http",
        "method": "POST",
        "path": "/auth/send-verification-email",
        "headers": [(b"origin", b"https://kakusui.org")],
        "client": ("203.0.113.20", 12345),
    })


def email_request(email="person@example.com"):
    return SendVerificationEmailRequest(
        email=email, clientID="browser-1", turnstile_token="test-token"
    )


@pytest.mark.asyncio
async def test_failed_turnstile_prevents_email_side_effects(email_flow):
    email_flow.verify_turnstile_token.side_effect = HTTPException(
        status_code=403, detail="Verification failed"
    )
    request = make_request()
    with pytest.raises(HTTPException) as error:
        await auth_route.send_verification_email_endpoint(email_request(), request)

    assert error.value.status_code == 403
    email_flow.enforce_otp_issue_source_limit.assert_called_once_with(request)
    email_flow.enforce_otp_issue_limits_after_verification.assert_not_called()
    email_flow.generate_verification_code.assert_not_awaited()
    email_flow.save_verification_data.assert_not_awaited()
    email_flow.send_verification_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_source_limit_runs_before_turnstile(email_flow):
    email_flow.enforce_otp_issue_source_limit.side_effect = HTTPException(
        status_code=429, detail="Too many requests"
    )
    with pytest.raises(HTTPException) as error:
        await auth_route.send_verification_email_endpoint(email_request(), make_request())
    assert error.value.status_code == 429
    email_flow.verify_turnstile_token.assert_not_awaited()
    email_flow.send_verification_email.assert_not_awaited()


@pytest.mark.asyncio
async def test_email_retry_is_rate_limited(email_flow):
    email_flow.enforce_otp_issue_limits_after_verification.side_effect = [
        None, HTTPException(status_code=429, detail="Too many verification emails",
                            headers={"Retry-After": "60"})
    ]
    first = await auth_route.send_verification_email_endpoint(email_request(), make_request())
    second = await auth_route.send_verification_email_endpoint(email_request(), make_request())
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["retry-after"] == "60"
    assert email_flow.verify_turnstile_token.await_count == 2
    email_flow.send_verification_email.assert_awaited_once_with("person@example.com", "123456")


@pytest.mark.asyncio
@pytest.mark.parametrize("email", ["registered@example.com", "new@example.com"])
async def test_success_does_not_disclose_registration(email_flow, monkeypatch, email):
    lookup = Mock(side_effect=AssertionError("Issuing a code must not look up registration"))
    monkeypatch.setattr(auth_route, "_find_user_by_email", lookup)
    request = make_request()
    response = await auth_route.send_verification_email_endpoint(email_request(email), request)
    assert response.status_code == 200
    assert json.loads(response.body) == {
        "message": "If the address can receive mail, a verification code was sent."
    }
    lookup.assert_not_called()
    email_flow.verify_turnstile_token.assert_awaited_once_with(
        "test-token", request, "verification_email"
    )
    email_flow.save_verification_data.assert_awaited_once_with(email, "123456")
    email_flow.send_verification_email.assert_awaited_once_with(email, "123456")
