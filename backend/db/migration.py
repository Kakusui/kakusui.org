## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

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
            print("users table not found. Attempting to create it.")
            User.__table__.create(engine)
            print("Created users table")
        else:
            print("users table already exists")

        inspector.clear_cache()

    except Exception as e:
        print(f"Error during migration 1: {str(e)}")

    ## Migration 2 (2024-09-05) (Addition of is_active column to users table)
    try:
        if(inspector.has_table('users')):
            columns = [c['name'] for c in inspector.get_columns('users')]
            if('is_active' not in columns):
                print("Adding is_active column to users table")
                with engine.begin() as connection:
                    connection.execute(text('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE'))
                print("Added is_active column to users table")
            else:
                print("is_active column already exists in users table")
        else:
            print("users table not found. Skipping is_active column addition.")
        
        inspector.clear_cache()
        
    except Exception as e:
        print(f"Error during migration 2: {str(e)}")