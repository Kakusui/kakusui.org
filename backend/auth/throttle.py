## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

from hashlib import sha256
import math
import time

from fastapi import HTTPException, Request, status
from sqlalchemy import case, delete, update
from sqlalchemy.exc import IntegrityError

from db.base import SessionLocal
from db.models import RequestRateLimit
from auth.client import get_request_client_identifier
from auth.verification import canonicalize_email


OTP_ISSUE_ACCOUNT_LIMIT = 5
OTP_ISSUE_GLOBAL_LIMIT = 200
OTP_ISSUE_SOURCE_LIMIT = 20
OTP_VERIFY_ACCOUNT_LIMIT = 12
OTP_VERIFY_GLOBAL_LIMIT = 600
OTP_VERIFY_SOURCE_LIMIT = 60
TURNSTILE_SOURCE_LIMIT = 60
TURNSTILE_GLOBAL_LIMIT = 600
GOOGLE_LOGIN_SOURCE_LIMIT = 10
GOOGLE_LOGIN_GLOBAL_LIMIT = 100
OTP_ISSUE_WINDOW_SECONDS = 3_600
OTP_VERIFY_WINDOW_SECONDS = 900
TURNSTILE_WINDOW_SECONDS = 60
GOOGLE_LOGIN_WINDOW_SECONDS = 60
RATE_LIMIT_RETENTION_SECONDS = 86_400


def _rate_limit_key(scope: str, identifier: str) -> str:
    return sha256(f"{scope}\0{identifier}".encode("utf-8")).hexdigest()


def consume_rate_limit(
    scope: str,
    identifier: str,
    *,
    limit: int,
    window_seconds: int,
) -> None:
    key = _rate_limit_key(scope, identifier)
    now = time.time()
    cutoff = now - window_seconds

    for _ in range(3):
        with SessionLocal() as db:
            reset_window = RequestRateLimit.window_started_at <= cutoff
            updated = db.execute(
                update(RequestRateLimit)
                .where(RequestRateLimit.key == key)
                .values(
                    count=case(
                        (reset_window, 1),
                        else_=RequestRateLimit.count + 1,
                    ),
                    window_started_at=case(
                        (reset_window, now),
                        else_=RequestRateLimit.window_started_at,
                    ),
                    updated_at=now,
                )
                .returning(RequestRateLimit.count, RequestRateLimit.window_started_at)
            ).one_or_none()

            if updated is None:
                try:
                    db.add(
                        RequestRateLimit(
                            key=key,
                            count=1,
                            window_started_at=now,
                            updated_at=now,
                        )
                    )
                    db.commit()
                    count, window_started_at = 1, now
                except IntegrityError:
                    db.rollback()
                    continue
            else:
                count, window_started_at = updated
                db.execute(
                    delete(RequestRateLimit).where(
                        RequestRateLimit.updated_at < now - RATE_LIMIT_RETENTION_SECONDS
                    )
                )
                db.commit()

            if count > limit:
                retry_after = max(1, math.ceil(window_started_at + window_seconds - now))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )
            return

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Unable to enforce request rate limit.",
    )


def enforce_otp_issue_source_limit(request: Request) -> None:
    consume_rate_limit(
        "otp-issue-source",
        get_request_client_identifier(request),
        limit=OTP_ISSUE_SOURCE_LIMIT,
        window_seconds=OTP_ISSUE_WINDOW_SECONDS,
    )


def enforce_otp_issue_limits_after_verification(email: str) -> None:
    consume_rate_limit(
        "otp-issue-global",
        "all",
        limit=OTP_ISSUE_GLOBAL_LIMIT,
        window_seconds=OTP_ISSUE_WINDOW_SECONDS,
    )
    consume_rate_limit(
        "otp-issue-account",
        canonicalize_email(email),
        limit=OTP_ISSUE_ACCOUNT_LIMIT,
        window_seconds=OTP_ISSUE_WINDOW_SECONDS,
    )


def enforce_otp_verify_limits(request: Request, email: str) -> None:
    consume_rate_limit(
        "otp-verify-source",
        get_request_client_identifier(request),
        limit=OTP_VERIFY_SOURCE_LIMIT,
        window_seconds=OTP_VERIFY_WINDOW_SECONDS,
    )
    consume_rate_limit(
        "otp-verify-global",
        "all",
        limit=OTP_VERIFY_GLOBAL_LIMIT,
        window_seconds=OTP_VERIFY_WINDOW_SECONDS,
    )
    consume_rate_limit(
        "otp-verify-account",
        canonicalize_email(email),
        limit=OTP_VERIFY_ACCOUNT_LIMIT,
        window_seconds=OTP_VERIFY_WINDOW_SECONDS,
    )


def enforce_turnstile_verification_limits(request: Request) -> None:
    """Bound outbound Siteverify calls before allocating an HTTP client."""
    consume_rate_limit(
        "turnstile-source",
        get_request_client_identifier(request),
        limit=TURNSTILE_SOURCE_LIMIT,
        window_seconds=TURNSTILE_WINDOW_SECONDS,
    )
    consume_rate_limit(
        "turnstile-global",
        "all",
        limit=TURNSTILE_GLOBAL_LIMIT,
        window_seconds=TURNSTILE_WINDOW_SECONDS,
    )


def enforce_google_login_limits(request: Request) -> None:
    consume_rate_limit(
        "google-login-source",
        get_request_client_identifier(request),
        limit=GOOGLE_LOGIN_SOURCE_LIMIT,
        window_seconds=GOOGLE_LOGIN_WINDOW_SECONDS,
    )
    consume_rate_limit(
        "google-login-global",
        "all",
        limit=GOOGLE_LOGIN_GLOBAL_LIMIT,
        window_seconds=GOOGLE_LOGIN_WINDOW_SECONDS,
    )


async def cleanup_expired_rate_limits() -> None:
    with SessionLocal() as db:
        db.execute(
            delete(RequestRateLimit).where(
                RequestRateLimit.updated_at < time.time() - RATE_LIMIT_RETENTION_SECONDS
            )
        )
        db.commit()
