## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

from dataclasses import dataclass
from enum import Enum
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from db.models import User


class CreditReservationStatus(Enum):
    RESERVED = "reserved"
    INVALID_USER = "invalid_user"
    INSUFFICIENT_CREDITS = "insufficient_credits"


@dataclass(frozen=True)
class CreditReservation:
    status: CreditReservationStatus
    user_id: Any | None = None
    balance: float | None = None


def reserve_credits(db: Session, email: str, cost: float) -> CreditReservation:
    """Atomically deduct cost when the user has a sufficient balance."""
    if cost <= 0:
        raise ValueError("Credit reservations must have a positive cost")

    user_id = db.execute(select(User.id).where(User.email == email)).scalar_one_or_none()
    if user_id is None:
        db.rollback()
        return CreditReservation(CreditReservationStatus.INVALID_USER)

    result = db.execute(
        update(User)
        .where(User.id == user_id, User.credits >= cost)
        .values(credits=User.credits - cost)
    )
    if result.rowcount != 1:
        db.rollback()
        return CreditReservation(
            CreditReservationStatus.INSUFFICIENT_CREDITS,
            user_id=user_id,
        )

    db.commit()
    balance = db.execute(select(User.credits).where(User.id == user_id)).scalar_one()
    return CreditReservation(
        CreditReservationStatus.RESERVED,
        user_id=user_id,
        balance=balance,
    )


def refund_credits(db: Session, user_id: Any, cost: float) -> float:
    """Atomically return a prior reservation and report the current balance."""
    if cost <= 0:
        raise ValueError("Credit refunds must have a positive cost")

    result = db.execute(
        update(User)
        .where(User.id == user_id)
        .values(credits=User.credits + cost)
    )
    if result.rowcount != 1:
        db.rollback()
        raise LookupError("Cannot refund credits for a missing user")

    db.commit()
    return db.execute(select(User.credits).where(User.id == user_id)).scalar_one()
