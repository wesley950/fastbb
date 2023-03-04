import os

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt

from app import crypto, models, schemas, dependencies
from app.environment import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    stored_user = db.query(models.StoredUser).filter(models.StoredUser.username == user.username).first()
    if stored_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use.")
    
    if user.email:
        stored_user = db.query(models.StoredUser).filter(models.StoredUser.email == user.email).first()
        if stored_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use.")

    hashed_password = crypto.hash_password(user.password)
    stored_user = models.StoredUser(username=user.username,
                                    email=user.email if user.email else None,
                                    hashed_password=hashed_password)
    db.add(stored_user)
    db.commit()
    db.refresh(stored_user)

    return stored_user


# @router.get("/{username}/", response_model=schemas.User)
# def read_user(username: str, db: Session = Depends(dependencies.get_db)):
#     stored_user = crud.get_user_by_name(db, username)
#     if not stored_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist.")
#     return stored_user


@router.get("/me")
async def read_users_me(current_user: models.User = Depends(dependencies.get_current_active_user)):
    return current_user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.StoredUser).filter(models.StoredUser.username == username).first()
    if not user:
        return False
    if not crypto.verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    jwt_encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return jwt_encoded


@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user.last_login = datetime.now()
    db.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token, "token_type": "bearer"
    }
