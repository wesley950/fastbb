from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str | None = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class PostBase(BaseModel):
    text: str
    parent_id: int | None = None


class Post(PostBase):
    id: int
    user_id: int
    children: list["Post"] = []

    class Config:
        orm_mode = True


class PostCreate(PostBase):
    pass
