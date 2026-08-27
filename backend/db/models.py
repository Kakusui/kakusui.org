## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
from uuid import uuid4
from datetime import datetime, timezone

## third-party imports
from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID as modelUUID

## custom imports
from db.base import Base

class EmailAlertModel(Base):
    __tablename__ = "email_alerts"
    id = Column(modelUUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    email = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class User(Base):
    __tablename__ = "users"
    id = Column(modelUUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    email = Column(String, unique=True, index=True)
    credits = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class StripePaymentFulfillment(Base):
    __tablename__ = "stripe_payment_fulfillments"
    __table_args__ = (
        CheckConstraint("credits_added > 0", name="ck_stripe_fulfillments_positive_credits"),
    )

    id = Column(modelUUID(as_uuid=True), primary_key=True, default=uuid4)
    stripe_session_id = Column(String, unique=True, nullable=False, index=True)
    stripe_payment_intent_id = Column(String, unique=True, nullable=False, index=True)
    user_email = Column(String, nullable=False, index=True)
    credits_added = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class EmailVerificationChallenge(Base):
    __tablename__ = "email_verification_challenges"

    email = Column(String, primary_key=True)
    code_digest = Column(String, nullable=False)
    expires_at = Column(Float, nullable=False, index=True)
    failed_attempts = Column(Integer, nullable=False, default=0)
    failure_window_started_at = Column(Float, nullable=False)

class RequestRateLimit(Base):
    __tablename__ = "request_rate_limits"

    key = Column(String, primary_key=True)
    count = Column(Integer, nullable=False, default=1)
    window_started_at = Column(Float, nullable=False)
    updated_at = Column(Float, nullable=False, index=True)

class EndpointStats(Base):
    __tablename__ = "endpoint_stats"
    id = Column(modelUUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    endpoint = Column(String, index=True)
    count = Column(Integer, default=0)
