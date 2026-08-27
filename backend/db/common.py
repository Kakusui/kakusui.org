## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import logging

## third-party imports
from filelock import FileLock
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.engine import Engine, Inspector
from sqlalchemy.exc import OperationalError

SCHEMA_LOCK_TIMEOUT_SECONDS = 60

def create_tables_if_not_exist(engine:Engine, base:DeclarativeMeta) -> None:
    inspector:Inspector = inspect(engine)
    for table_name in base.metadata.tables.keys():

        try:
            if(not inspector.has_table(table_name)):
                base.metadata.tables[table_name].create(engine)

        except OperationalError:
            # SQLAlchemy wraps the driver's sqlite3 error. Ignore a competing
            # CREATE only when a fresh inspection proves the table now exists.
            if(not inspect(engine).has_table(table_name)):
                raise

            logging.warning(
                "Table %s was created by another process during initialization",
                table_name,
            )

def initialize_database_schema(
    engine:Engine,
    base:DeclarativeMeta,
    database_path:str,
) -> None:
    from db.migration import migrate_database

    schema_lock = FileLock(
        f"{database_path}.schema.lock",
        timeout=SCHEMA_LOCK_TIMEOUT_SECONDS,
    )
    with schema_lock:
        create_tables_if_not_exist(engine, base)
        migrate_database(engine)
