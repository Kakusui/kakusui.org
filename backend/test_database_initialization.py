import os
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock, patch

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from db.base import Base
from db.common import create_tables_if_not_exist, initialize_database_schema
import db.common as db_common
import db.migration as db_migration


class DatabaseInitializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "kakusui.db"
        self.database_url = f"sqlite:///{self.database_path}"
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False},
        )

    def tearDown(self) -> None:
        self.engine.dispose()
        self.temp_dir.cleanup()

    def test_initialization_creates_tables_and_seed_rows(self) -> None:
        initialize_database_schema(self.engine, Base, str(self.database_path))

        with self.engine.connect() as connection:
            table_names = {
                row[0]
                for row in connection.execute(
                    text("SELECT name FROM sqlite_master WHERE type = 'table'")
                )
            }
            endpoints = connection.execute(
                text("SELECT endpoint FROM endpoint_stats ORDER BY endpoint")
            ).scalars().all()

        self.assertTrue(
            {
                "email_alerts",
                "users",
                "stripe_payment_fulfillments",
                "endpoint_stats",
            }.issubset(table_names)
        )
        self.assertEqual(endpoints, ["EasyTL", "Elucidate", "Kairyou"])

    def test_repeated_initialization_does_not_duplicate_seed_rows(self) -> None:
        initialize_database_schema(self.engine, Base, str(self.database_path))
        initialize_database_schema(self.engine, Base, str(self.database_path))

        with self.engine.connect() as connection:
            endpoint_counts = connection.execute(
                text(
                    "SELECT endpoint, COUNT(*) FROM endpoint_stats "
                    "GROUP BY endpoint ORDER BY endpoint"
                )
            ).all()

        self.assertEqual(
            endpoint_counts,
            [("EasyTL", 1), ("Elucidate", 1), ("Kairyou", 1)],
        )

    def test_initialization_upgrades_an_old_users_schema(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(text(
                "CREATE TABLE users ("
                "id VARCHAR NOT NULL PRIMARY KEY, "
                "email VARCHAR UNIQUE, "
                "credits INTEGER DEFAULT 0)"
            ))

        initialize_database_schema(self.engine, Base, str(self.database_path))

        with self.engine.connect() as connection:
            user_columns = {
                row[1]
                for row in connection.execute(text("PRAGMA table_info(users)"))
            }
            fulfillment_table = connection.execute(text(
                "SELECT COUNT(*) FROM sqlite_master "
                "WHERE type = 'table' AND name = 'stripe_payment_fulfillments'"
            )).scalar_one()

        self.assertIn("is_active", user_columns)
        self.assertEqual(fulfillment_table, 1)

    def test_concurrent_initialization_serializes_migrations(self) -> None:
        second_engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False},
        )
        start_barrier = threading.Barrier(2)
        state_lock = threading.Lock()
        active_migrations = 0
        maximum_active_migrations = 0
        migration_calls = 0

        def tracked_migration(_engine) -> None:
            nonlocal active_migrations
            nonlocal maximum_active_migrations
            nonlocal migration_calls
            with state_lock:
                active_migrations += 1
                migration_calls += 1
                maximum_active_migrations = max(
                    maximum_active_migrations,
                    active_migrations,
                )
            time.sleep(0.1)
            with state_lock:
                active_migrations -= 1

        def initialize(engine) -> None:
            start_barrier.wait()
            initialize_database_schema(engine, Base, str(self.database_path))

        try:
            with patch.object(
                db_migration,
                "migrate_database",
                side_effect=tracked_migration,
            ):
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [
                        executor.submit(initialize, self.engine),
                        executor.submit(initialize, second_engine),
                    ]
                    for future in futures:
                        future.result(timeout=5)
        finally:
            second_engine.dispose()

        self.assertEqual(migration_calls, 2)
        self.assertEqual(maximum_active_migrations, 1)


class CreateTablesOperationalErrorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = Mock()
        self.table = Mock()
        self.table.create.side_effect = OperationalError(
            "CREATE TABLE example",
            {},
            Exception("database error"),
        )
        self.base = Mock()
        self.base.metadata.tables = {"example": self.table}
        self.initial_inspector = Mock()
        self.initial_inspector.has_table.return_value = False

    def test_ignores_operational_error_when_table_now_exists(self) -> None:
        post_error_inspector = Mock()
        post_error_inspector.has_table.return_value = True

        with patch.object(
            db_common,
            "inspect",
            side_effect=[self.initial_inspector, post_error_inspector],
        ):
            create_tables_if_not_exist(self.engine, self.base)

    def test_reraises_operational_error_when_table_is_still_missing(self) -> None:
        post_error_inspector = Mock()
        post_error_inspector.has_table.return_value = False

        with patch.object(
            db_common,
            "inspect",
            side_effect=[self.initial_inspector, post_error_inspector],
        ):
            with self.assertRaises(OperationalError):
                create_tables_if_not_exist(self.engine, self.base)


if __name__ == "__main__":
    unittest.main()
