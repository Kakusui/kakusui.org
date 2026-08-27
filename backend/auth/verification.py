## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

from datetime import datetime
from hashlib import sha256
import hmac
import time

from sqlalchemy import case, delete, or_, select, update
from sqlalchemy.exc import IntegrityError

from constants import (
    ACCESS_TOKEN_SECRET,
    MAX_EMAIL_VERIFICATION_ATTEMPTS,
    RATE_LIMIT_WINDOW,
    VERIFICATION_EXPIRATION_MINUTES,
)
from db.base import SessionLocal
from db.models import EmailVerificationChallenge


class VerificationAttemptsExceeded(RuntimeError):
    pass


def canonicalize_email(email: str) -> str:
    stripped_email = email.strip()
    local_part, separator, domain = stripped_email.rpartition("@")
    if not separator or not local_part or not domain:
        raise ValueError("Invalid email address")
    return f"{local_part}@{domain.casefold()}"


def _code_digest(email: str, code: str) -> str:
    if not ACCESS_TOKEN_SECRET:
        raise RuntimeError("ACCESS_TOKEN_SECRET is required for verification codes")
    message = f"kakusui-email-verification\0{canonicalize_email(email)}\0{code}"
    return hmac.new(
        ACCESS_TOKEN_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        sha256,
    ).hexdigest()


def save_verification_data(
    email: str,
    code: str,
    existing_data: dict | None = None,
) -> None:
    """Replace an OTP without resetting its account failure window."""
    del existing_data  # Retained in the signature for older internal callers.

    normalized_email = canonicalize_email(email)
    now = time.time()
    failure_cutoff = now - RATE_LIMIT_WINDOW
    expires_at = now + VERIFICATION_EXPIRATION_MINUTES * 60
    digest = _code_digest(normalized_email, code)

    for _ in range(3):
        with SessionLocal() as db:
            reset_window = EmailVerificationChallenge.failure_window_started_at <= failure_cutoff
            result = db.execute(
                update(EmailVerificationChallenge)
                .where(
                    EmailVerificationChallenge.email == normalized_email,
                    or_(
                        EmailVerificationChallenge.failed_attempts < MAX_EMAIL_VERIFICATION_ATTEMPTS,
                        reset_window,
                    ),
                )
                .values(
                    code_digest=digest,
                    expires_at=expires_at,
                    failed_attempts=case(
                        (reset_window, 0),
                        else_=EmailVerificationChallenge.failed_attempts,
                    ),
                    failure_window_started_at=case(
                        (reset_window, now),
                        else_=EmailVerificationChallenge.failure_window_started_at,
                    ),
                )
            )
            if result.rowcount == 1:
                db.commit()
                return

            try:
                db.add(
                    EmailVerificationChallenge(
                        email=normalized_email,
                        code_digest=digest,
                        expires_at=expires_at,
                        failed_attempts=0,
                        failure_window_started_at=now,
                    )
                )
                db.commit()
                return
            except IntegrityError:
                db.rollback()
                existing = db.execute(
                    select(EmailVerificationChallenge.failed_attempts).where(
                        EmailVerificationChallenge.email == normalized_email
                    )
                ).scalar_one_or_none()
                if existing is not None and existing >= MAX_EMAIL_VERIFICATION_ATTEMPTS:
                    raise VerificationAttemptsExceeded(
                        "Too many verification attempts. Please try again later."
                    )

    raise RuntimeError("Unable to update verification challenge")


def verify_verification_code(email: str, verification_code: str) -> bool:
    normalized_email = canonicalize_email(email)
    now = time.time()
    failure_cutoff = now - RATE_LIMIT_WINDOW
    digest = _code_digest(normalized_email, verification_code)

    with SessionLocal() as db:
        db.execute(
            update(EmailVerificationChallenge)
            .where(
                EmailVerificationChallenge.email == normalized_email,
                EmailVerificationChallenge.failure_window_started_at <= failure_cutoff,
            )
            .values(failed_attempts=0, failure_window_started_at=now)
        )

        accepted = db.execute(
            delete(EmailVerificationChallenge).where(
                EmailVerificationChallenge.email == normalized_email,
                EmailVerificationChallenge.code_digest == digest,
                EmailVerificationChallenge.expires_at > now,
                EmailVerificationChallenge.failed_attempts < MAX_EMAIL_VERIFICATION_ATTEMPTS,
            )
        )
        if accepted.rowcount == 1:
            db.commit()
            return True

        rejected = db.execute(
            update(EmailVerificationChallenge)
            .where(
                EmailVerificationChallenge.email == normalized_email,
                EmailVerificationChallenge.expires_at > now,
                EmailVerificationChallenge.failed_attempts < MAX_EMAIL_VERIFICATION_ATTEMPTS,
            )
            .values(failed_attempts=EmailVerificationChallenge.failed_attempts + 1)
        )
        if rejected.rowcount == 1:
            db.commit()
            return False

        attempts = db.execute(
            select(EmailVerificationChallenge.failed_attempts).where(
                EmailVerificationChallenge.email == normalized_email,
                EmailVerificationChallenge.expires_at > now,
            )
        ).scalar_one_or_none()
        db.commit()
        if attempts is not None and attempts >= MAX_EMAIL_VERIFICATION_ATTEMPTS:
            raise VerificationAttemptsExceeded(
                "Too many verification attempts. Please try again later."
            )
        return False


def remove_verification_data(email: str) -> None:
    with SessionLocal() as db:
        db.execute(
            delete(EmailVerificationChallenge).where(
                EmailVerificationChallenge.email == canonicalize_email(email)
            )
        )
        db.commit()


def get_verification_data(email: str) -> dict | None:
    """Return non-secret challenge metadata for legacy internal callers."""
    with SessionLocal() as db:
        challenge = db.execute(
            select(EmailVerificationChallenge).where(
                EmailVerificationChallenge.email == canonicalize_email(email)
            )
        ).scalar_one_or_none()
        if challenge is None:
            return None
        return {
            "expiration": datetime.fromtimestamp(challenge.expires_at).isoformat(),
            "attempts": challenge.failed_attempts,
        }


def cleanup_expired_verification_data() -> None:
    now = time.time()
    failure_cutoff = now - RATE_LIMIT_WINDOW
    with SessionLocal() as db:
        db.execute(
            delete(EmailVerificationChallenge).where(
                EmailVerificationChallenge.expires_at <= now,
                EmailVerificationChallenge.failure_window_started_at <= failure_cutoff,
            )
        )
        db.commit()
