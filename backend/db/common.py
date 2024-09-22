## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## third-party imports
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.engine import Engine, Inspector

from sqlite3 import OperationalError

def create_tables_if_not_exist(engine:Engine, base:DeclarativeMeta) -> None:
    inspector:Inspector = inspect(engine)
    for table_name in base.metadata.tables.keys():

        try:

            if(not inspector.has_table(table_name)):
                base.metadata.tables[table_name].create(engine)

        except OperationalError:
            print(f"Tried creating table {table_name}, but failed. SAFE TO IGNORE")