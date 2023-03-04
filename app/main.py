from fastapi import FastAPI

from . import models
from .database import engine
from .routers import users, posts


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(posts.router)


@app.get("/")
async def home():
    return {"message": "Hello, world!!! Welcome to the home page."}
