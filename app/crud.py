from sqlalchemy.orm import Session

from . import models, schemas, crypto


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = crypto.hash(user.password)
    stored_user = models.User(username=user.username,
                              hashed_password=hashed_password)
    db.add(stored_user)
    db.commit()
    db.refresh(stored_user)
    return stored_user


def create_item(db: Session, item: schemas.ItemCreate, user_id: int):
    stored_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(stored_item)
    db.commit()
    db.refresh(stored_item)
    return stored_item
