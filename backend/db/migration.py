## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import logging
import uuid

## third-party imports
from sqlalchemy import Engine, text
from sqlalchemy.inspection import inspect

## custom imports
from db.models import User, EndpointStats
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
            logging.info("[Migration 1] [1/1] [Passed] Created users table")
        else:
            logging.info("[Migration 1] [1/1] [Skipped] users table already exists")

        inspector.clear_cache()

    except Exception as e:
        logging.error(f"[Migration 1] [Failed] {str(e)}")

    ## Migration 2 (2024-09-05) (Addition of is_active column to users table)
    try:

        columns = [c['name'] for c in inspector.get_columns('users')]
        if('is_active' not in columns):
            with engine.begin() as connection:
                connection.execute(text('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE'))
            logging.info("[Migration 2] [1/1] [Passed] Added is_active column to users table")
        else:
            logging.info("[Migration 2] [1/1] [Skipped] is_active column already exists in users table")

        inspector.clear_cache()

    except Exception as e:
        logging.error(f"[Migration 2] [Failed] {str(e)}")

    ## Migration 3 (2024-10-22) (Addition of endpoint_stats table and initial entries)
    try:
        if(not inspector.has_table('endpoint_stats')):
            ## create the table
            EndpointStats.__table__.create(engine)
            logging.info("[Migration 3] [1/2] [Passed] Created endpoint_stats table")
        else:
            logging.info("[Migration 3] [1/2] [Skipped] endpoint_stats table already exists")

        ## Check and add entries for Kairyou, Elucidate, and EasyTL
        with engine.connect() as connection:
            for endpoint in ["Kairyou", "Elucidate", "EasyTL"]:
                result = connection.execute(text(f"SELECT COUNT(*) FROM endpoint_stats WHERE endpoint = '{endpoint}'"))
                count = result.scalar()
                
                if(count == 0):
                    connection.execute(text(f"INSERT INTO endpoint_stats (id, endpoint, count) VALUES ('{uuid.uuid4()}', '{endpoint}', 0)"))
                    connection.commit()
                    logging.info(f"[Migration 3] [2/2] [Passed] Added {endpoint} entry to endpoint_stats table")
                else:
                    logging.info(f"[Migration 3] [2/2] [Skipped] {endpoint} entry already exists in endpoint_stats table")

        inspector.clear_cache()

    except Exception as e:
        logging.error(f"[Migration 3] [Failed] {str(e)}")
