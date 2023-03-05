from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from fastbb import dependencies, models, schemas


router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.post("/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not logged in."
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Deactivated user."
        )

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not an admin."
        )

    if not category.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name can not be empty."
        )

    stored_category = db.query(models.Category).filter(
        models.Category.name == category.name).first()
    if stored_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists."
        )

    stored_category = models.Category(
        name=category.name
    )
    db.add(stored_category)
    db.commit()
    db.refresh(stored_category)

    return stored_category


@router.get("/", response_model=list[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    return db.query(models.Category).offset(skip).limit(limit).all()
