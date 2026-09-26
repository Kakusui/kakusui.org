import asyncio
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.models import StripePaymentFulfillment, User
from routes import financial
from routes.financial import (
    PaymentFulfillmentConflictError,
    PaymentUserNotFoundError,
    record_payment_fulfillment,
)


class FakeRequest:
    def __init__(self, session_id):
        self.session_id = session_id

    async def json(self):
        return {"session_id": self.session_id}


class StripeFulfillmentSecurityTests(unittest.TestCase):
    def setUp(self):
        stripe_mock = SimpleNamespace(
            checkout=SimpleNamespace(Session=SimpleNamespace()),
            PaymentIntent=SimpleNamespace(),
        )
        stripe_patch = patch.object(financial, "stripe", stripe_mock)
        stripe_patch.start()
        self.addCleanup(stripe_patch.stop)
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "stripe-test.db"
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False, "timeout": 10},
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.email = "buyer@example.com"
        with self.Session() as db:
            db.add(User(email=self.email, credits=100))
            db.commit()

    def tearDown(self):
        self.engine.dispose()
        self.temp_dir.cleanup()

    def balance_and_fulfillment_count(self):
        with self.Session() as db:
            balance = db.execute(
                select(User.credits).where(User.email == self.email)
            ).scalar_one()
            count = db.execute(
                select(func.count()).select_from(StripePaymentFulfillment)
            ).scalar_one()
            return balance, count

    def test_exact_retry_credits_once(self):
        with self.Session() as db:
            first = record_payment_fulfillment(db, "cs_1", "pi_1", self.email, 50000)
        with self.Session() as db:
            retry = record_payment_fulfillment(db, "cs_1", "pi_1", self.email, 50000)

        self.assertTrue(first)
        self.assertFalse(retry)
        self.assertEqual(self.balance_and_fulfillment_count(), (50100, 1))

    def test_concurrent_retry_credits_once(self):
        barrier = threading.Barrier(2)

        def fulfill():
            with self.Session() as db:
                barrier.wait()
                return record_payment_fulfillment(
                    db, "cs_concurrent", "pi_concurrent", self.email, 50000
                )

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: fulfill(), range(2)))

        self.assertEqual(sorted(results), [False, True])
        self.assertEqual(self.balance_and_fulfillment_count(), (50100, 1))

    def test_reused_payment_intent_is_a_conflict(self):
        with self.Session() as db:
            record_payment_fulfillment(db, "cs_original", "pi_shared", self.email, 50000)

        with self.Session() as db:
            with self.assertRaises(PaymentFulfillmentConflictError):
                record_payment_fulfillment(db, "cs_other", "pi_shared", self.email, 50000)

        self.assertEqual(self.balance_and_fulfillment_count(), (50100, 1))

    def test_missing_user_rolls_back_ledger(self):
        with self.Session() as db:
            with self.assertRaises(PaymentUserNotFoundError):
                record_payment_fulfillment(
                    db, "cs_missing", "pi_missing", "missing@example.com", 50000
                )

        self.assertEqual(self.balance_and_fulfillment_count(), (100, 0))

    def test_legacy_stripe_processed_marker_prevents_recredit(self):
        financial.stripe.checkout.Session.retrieve = lambda _: SimpleNamespace(
            id="cs_legacy",
            payment_status="paid",
            client_reference_id=self.email,
            payment_intent="pi_legacy",
            metadata={"credits_to_add": "50000"},
        )
        financial.stripe.PaymentIntent.retrieve = lambda _: SimpleNamespace(
            metadata={"processed": "true"}
        )
        financial.stripe.PaymentIntent.modify = lambda *_args, **_kwargs: self.fail(
            "legacy payments must not be modified or credited"
        )

        with self.Session() as db:
            result = asyncio.run(
                financial.verify_payment(FakeRequest("cs_legacy"), db, self.email)
            )

        self.assertEqual(result, {"success": True, "message": "Payment already processed."})
        self.assertEqual(self.balance_and_fulfillment_count(), (100, 0))

    def test_unpaid_or_mismatched_session_is_never_fulfilled(self):
        financial.stripe.PaymentIntent.retrieve = lambda _: self.fail(
            "rejected sessions must not reach PaymentIntent retrieval"
        )

        rejected_sessions = (
            SimpleNamespace(
                id="cs_unpaid",
                payment_status="unpaid",
                client_reference_id=self.email,
            ),
            SimpleNamespace(
                id="cs_other_user",
                payment_status="paid",
                client_reference_id="other@example.com",
            ),
        )

        for checkout_session in rejected_sessions:
            with self.subTest(session_id=checkout_session.id):
                financial.stripe.checkout.Session.retrieve = lambda _, value=checkout_session: value
                with self.Session() as db:
                    result = asyncio.run(
                        financial.verify_payment(FakeRequest(checkout_session.id), db, self.email)
                    )
                self.assertEqual(
                    result,
                    {"success": False, "message": "Payment not completed or user mismatch."},
                )

        self.assertEqual(self.balance_and_fulfillment_count(), (100, 0))

    def test_remote_marker_failure_does_not_undo_local_fulfillment(self):
        financial.stripe.checkout.Session.retrieve = lambda _: SimpleNamespace(
            id="cs_new",
            payment_status="paid",
            client_reference_id=self.email,
            payment_intent="pi_new",
            metadata={"credits_to_add": "50000"},
        )
        financial.stripe.PaymentIntent.retrieve = lambda _: SimpleNamespace(metadata={})

        def fail_remote_marker(*_args, **_kwargs):
            raise RuntimeError("Stripe unavailable after local commit")

        financial.stripe.PaymentIntent.modify = fail_remote_marker

        with self.Session() as db:
            first = asyncio.run(financial.verify_payment(FakeRequest("cs_new"), db, self.email))
        with self.Session() as db:
            retry = asyncio.run(financial.verify_payment(FakeRequest("cs_new"), db, self.email))

        self.assertTrue(first["success"])
        self.assertEqual(retry, {"success": True, "message": "Payment already processed."})
        self.assertEqual(self.balance_and_fulfillment_count(), (50100, 1))

    def test_local_retry_does_not_depend_on_payment_intent_retrieval(self):
        with self.Session() as db:
            record_payment_fulfillment(db, "cs_local", "pi_local", self.email, 50000)

        financial.stripe.checkout.Session.retrieve = lambda _: SimpleNamespace(
            id="cs_local",
            payment_status="paid",
            client_reference_id=self.email,
            payment_intent="pi_local",
            metadata={"credits_to_add": "50000"},
        )
        financial.stripe.PaymentIntent.retrieve = lambda _: self.fail(
            "an exact local retry must not depend on Stripe PaymentIntent retrieval"
        )
        processed_markers = []
        financial.stripe.PaymentIntent.modify = lambda payment_intent_id, metadata: (
            processed_markers.append((payment_intent_id, metadata))
        )

        with self.Session() as db:
            result = asyncio.run(
                financial.verify_payment(FakeRequest("cs_local"), db, self.email)
            )

        self.assertEqual(result, {"success": True, "message": "Payment already processed."})
        self.assertEqual(self.balance_and_fulfillment_count(), (50100, 1))
        self.assertEqual(processed_markers, [("pi_local", {"processed": "true"})])


if __name__ == "__main__":
    unittest.main()
