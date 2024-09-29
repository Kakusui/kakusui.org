## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

## built-in imports
from uuid import uuid4
from datetime import datetime, timezone

## third-party imports
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as modelUUID

## custom imports
from db.base import Base

class EmailAlertModel(Base):
    __tablename__ = "email_alerts"
    id = Column(modelUUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    email = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class User(Base):
    __tablename__ = "users"
    id = Column(modelUUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    email = Column(String, unique=True, index=True)
    credits = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)