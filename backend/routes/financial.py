## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import stripe

## custom modules
from db.base import get_db
from db.models import User
from auth.func import get_current_user
from util import get_frontend_url
from auth.util import check_internal_request
router = APIRouter()

@router.post("/stripe/create-checkout-session")
async def create_checkout_session(request: Request, current_user: str = Depends(get_current_user)):
    
    await check_internal_request(request)

    FRONTEND_URL = await get_frontend_url()

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
            success_url=f'{FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{FRONTEND_URL}/pricing',
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
    
    await check_internal_request(request)

    if(not current_user):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not logged in")

    try:
        data = await request.json()
        session_id = data.get('session_id')
        
        if(not session_id):
            return {"success": False, "message": "No session ID provided."}

        session = stripe.checkout.Session.retrieve(session_id)

        if(session.payment_status == 'paid' and session.client_reference_id == current_user):
            user = db.query(User).filter(User.email == current_user).first()
            if(user):
                payment_intent_id = session.payment_intent
                if(not payment_intent_id):
                    return {"success": False, "message": "No payment intent found."}

                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id) # type: ignore

                if(not payment_intent.metadata.get('processed')):
                    credits_to_add = int(session.metadata.get('credits_to_add', 0)) # type: ignore
                    user.credits = user.credits + credits_to_add # type: ignore
                    db.commit()

                    stripe.PaymentIntent.modify(
                        payment_intent_id, # type: ignore
                        metadata={'processed': 'true'}
                    )

                    return {"success": True, "message": f"Payment verified and {credits_to_add} credits added."}
                else:
                    return {"success": True, "message": "Payment already processed."}
            else:
                return {"success": False, "message": "User not found."}
        else:
            return {"success": False, "message": "Payment not completed or user mismatch."}
    except Exception as e:
        return {"success": False, "message": str(e)}