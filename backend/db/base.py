## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
import typing

## third-party imports
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import create_engine, Engine

## custom imports
from constants import DATABASE_URL

Base:DeclarativeMeta = declarative_base()
engine:Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal:sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db() -> typing.AsyncGenerator[Session, None]:
    
    """

    Get the database session.

    Returns:
    typing.AsyncGenerator[Session, None]: The database session

    """

    db:Session = SessionLocal()
    
    try:
        yield db
    
    finally:
        db.close()