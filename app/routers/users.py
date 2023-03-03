import os

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app import crud, crypto, models, schemas
from app.database import SessionLocal


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    stored_user = crud.get_user_by_name(db, user.username)
    if stored_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use.")
    return crud.create_user(db, user)


@router.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_users(db, skip, limit)


@router.get("/users/{username}/", response_model=schemas.User)
def read_user(username: str, db: Session = Depends(get_db)):
    stored_user = crud.get_user_by_name(db, username)
    if not stored_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist.")
    return stored_user


def get_user(db: Session, username: str):
    stored_user = crud.get_user_by_name(db, username)
    return stored_user


def get_stored_user(db: Session, username: str):
    stored_user = crud.get_stored_user_by_name(db, username)
    return stored_user


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(db, token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user.")
    return current_user


@router.get("/users/me")
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_stored_user(db, username)
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


@router.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token, "token_type": "bearer"
    }
