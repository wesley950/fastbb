from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

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

    posts = relationship("Post", back_populates="user")


class StoredUser(User):
    hashed_password = Column(String)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    add_date = Column(DateTime, default=datetime.now)

    posts = relationship("Post", back_populates="category")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    reg_date = Column(DateTime, default=datetime.now)

    user_id = Column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="posts")

    category_id = Column(ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="posts")

    children = relationship("Post", back_populates="parent")

    parent_id = Column(ForeignKey("posts.id"))
    parent = relationship("Post", back_populates="children", remote_side=[id])
