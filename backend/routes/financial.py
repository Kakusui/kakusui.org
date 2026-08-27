## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import logging

## third-party imports
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import stripe

## custom modules
from db.base import get_db
from db.models import StripePaymentFulfillment, User
from auth.func import get_current_user
from util import get_frontend_url
from .models import StripeCheckoutRequest

router = APIRouter()
logger = logging.getLogger(__name__)

class PaymentFulfillmentConflictError(Exception):
    pass

class PaymentUserNotFoundError(Exception):
    pass

def is_payment_fulfilled(
    db: Session,
    stripe_session_id: str,
    stripe_payment_intent_id: str,
    user_email: str,
    credits_to_add: int,
) -> bool:
    existing = db.query(StripePaymentFulfillment).filter(
        or_(
            StripePaymentFulfillment.stripe_session_id == stripe_session_id,
            StripePaymentFulfillment.stripe_payment_intent_id == stripe_payment_intent_id,
        )
    ).first()
    is_exact_match = bool(
        existing
        and existing.stripe_session_id == stripe_session_id
        and existing.stripe_payment_intent_id == stripe_payment_intent_id
        and existing.user_email == user_email
        and existing.credits_added == credits_to_add
    )
    db.rollback()

    if(existing and not is_exact_match):
        raise PaymentFulfillmentConflictError()

    return is_exact_match

def record_payment_fulfillment(
    db: Session,
    stripe_session_id: str,
    stripe_payment_intent_id: str,
    user_email: str,
    credits_to_add: int,
) -> bool:
    """Atomically record a Stripe payment and credit its owning user.

    Returns True when credits were added and False for an exact retry.
    """

    if(credits_to_add <= 0):
        raise ValueError("credits_to_add must be positive")

    fulfillment = StripePaymentFulfillment(
        stripe_session_id=stripe_session_id,
        stripe_payment_intent_id=stripe_payment_intent_id,
        user_email=user_email,
        credits_added=credits_to_add,
    )

    try:
        db.add(fulfillment)
        db.flush()

        result = db.execute(
            update(User)
            .where(User.email == user_email)
            .values(credits=User.credits + credits_to_add)
        )
        if(result.rowcount != 1):
            raise PaymentUserNotFoundError()

        db.commit()
        return True

    except IntegrityError as error:
        db.rollback()
        if(is_payment_fulfilled(
            db,
            stripe_session_id,
            stripe_payment_intent_id,
            user_email,
            credits_to_add,
        )):
            return False

        raise PaymentFulfillmentConflictError() from error

    except Exception:
        db.rollback()
        raise


def mark_payment_intent_processed(payment_intent_id: str) -> None:
    """Best-effort synchronization for deployments that predate the local ledger."""
    try:
        stripe.PaymentIntent.modify(
            payment_intent_id,
            metadata={'processed': 'true'}
        )
    except Exception:
        logger.warning("Unable to synchronize Stripe processed marker for %s", payment_intent_id)

@router.post("/stripe/create-checkout-session")
async def create_checkout_session(
    request: Request, 
    checkout_request: StripeCheckoutRequest,
    current_user: str = Depends(get_current_user)
):
    FRONTEND_URL = await get_frontend_url(is_home_page=checkout_request.is_home_page)

    if(checkout_request.is_home_page):

        success_url = f'{FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}'
        cancel_url = f'{FRONTEND_URL}/pricing'

    else:
        success_url = f'{FRONTEND_URL}?verify_session_id={{CHECKOUT_SESSION_ID}}'
        cancel_url = f'{FRONTEND_URL}'

    if(not current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not logged in")

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': 500,
                        'product_data': {
                            'name': '50,000 Kakusui Credits',
                            'description': 'Credits for use with Kakusui services',
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=current_user,
            metadata={
                'credits_to_add': '50000'
            },
            customer_email=current_user
        )
        return {"id": checkout_session.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stripe/verify-payment")
async def verify_payment(request: Request, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    if(not current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not logged in")

    try:
        data = await request.json()
        session_id = data.get('session_id')
        
        if(not session_id):
            return {"success": False, "message": "No session ID provided."}

        checkout_session = stripe.checkout.Session.retrieve(session_id)

        if(checkout_session.payment_status != 'paid' or checkout_session.client_reference_id != current_user):
            return {"success": False, "message": "Payment not completed or user mismatch."}

        payment_intent = checkout_session.payment_intent
        payment_intent_id = getattr(payment_intent, "id", payment_intent)
        if(not payment_intent_id or not isinstance(payment_intent_id, str)):
            return {"success": False, "message": "No payment intent found."}

        stripe_session_id = getattr(checkout_session, "id", session_id)
        if(not stripe_session_id or not isinstance(stripe_session_id, str)):
            return {"success": False, "message": "Invalid payment session."}

        credits_to_add = int(checkout_session.metadata.get('credits_to_add', 0))
        try:
            if(is_payment_fulfilled(
                db,
                stripe_session_id,
                payment_intent_id,
                current_user,
                credits_to_add,
            )):
                mark_payment_intent_processed(payment_intent_id)
                return {"success": True, "message": "Payment already processed."}
        except PaymentFulfillmentConflictError:
            return {"success": False, "message": "Payment fulfillment conflict."}

        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        # Payments fulfilled before the local ledger existed are marked only in Stripe.
        if(payment_intent.metadata.get('processed')):
            return {"success": True, "message": "Payment already processed."}

        try:
            credits_added = record_payment_fulfillment(
                db,
                stripe_session_id,
                payment_intent_id,
                current_user,
                credits_to_add,
            )
        except PaymentUserNotFoundError:
            return {"success": False, "message": "User not found."}
        except PaymentFulfillmentConflictError:
            return {"success": False, "message": "Payment fulfillment conflict."}

        if(not credits_added):
            mark_payment_intent_processed(payment_intent_id)
            return {"success": True, "message": "Payment already processed."}

        mark_payment_intent_processed(payment_intent_id)

        return {"success": True, "message": f"Payment verified and {credits_to_add} credits added."}

    except Exception:
        db.rollback()
        return {"success": False, "message": f"An error occurred"}
