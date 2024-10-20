## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import logging

## third-party imports
from sqlalchemy import Engine, text
from sqlalchemy.inspection import inspect

## custom imports
from db.models import User

def migrate_database(engine:Engine) -> None:

    """

    Performs database migrations if needed.
    
    """

    inspector = inspect(engine)

    inspector.clear_cache()

    ## Migration 1 (2024-09-05) (Addition of users table)
    try:
        if(not inspector.has_table('users')):
            User.__table__.create(engine)
            logging.info("[Migration 1] [Passed] Created users table")
        else:
            logging.info("[Migration 1] [Skipped] users table already exists")

        inspector.clear_cache()

    except Exception as e:
        logging.error(f"[Migration 1] [Failed] {str(e)}")

    ## Migration 2 (2024-09-05) (Addition of is_active column to users table)
    try:

        columns = [c['name'] for c in inspector.get_columns('users')]
        if('is_active' not in columns):
            with engine.begin() as connection:
                connection.execute(text('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE'))
            logging.info("[Migration 2] [Passed] Added is_active column to users table")
        else:
            logging.info("[Migration 2] [Skipped] is_active column already exists in users table")

        inspector.clear_cache()

    except Exception as e:
        logging.error(f"[Migration 2] [Failed] {str(e)}")