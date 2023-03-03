from fastapi import APIRouter


router = APIRouter(
    prefix="/quotes",
    tags=["quotes"]
)


@router.get("/")
async def read_quotes():
    return [
        "Test",
        "Hello, world!!!"
    ]
