from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    reg_date = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)


class StoredUser(User):
    hashed_password = Column(String)
