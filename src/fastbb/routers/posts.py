from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from fastbb import dependencies, models, schemas


router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.post("/", response_model=schemas.Post)
def create_user_post(post: schemas.PostCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
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

    if not post.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post text can not be empty."
        )

    if not post.category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post category can not be empty."
        )

    stored_category = db.query(models.Category).filter(
        models.Category.name == post.category).first()
    if not stored_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    if post.parent_id:
        stored_parent = db.query(models.Post).filter(models.Post.id == post.parent_id).first()
        if not stored_parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid parent post."
            )

    stored_post = models.Post(
        text=post.text,
        user_id=current_user.id,
        category_id=stored_category.id,
        parent_id=post.parent_id if post.parent_id else None
    )
    db.add(stored_post)
    db.commit()
    db.refresh(stored_post)

    return stored_post


@router.get("/category/{category_name}", response_model=list[schemas.Post])
def read_category_posts(category_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    stored_category = db.query(models.Category).filter(models.Category.name == category_name).first()
    if not stored_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )
    
    posts = db.query(models.Post).filter(models.Post.category_id == stored_category.id).offset(skip).limit(limit).all()
    return posts


@router.get("/user/{username}", response_model=list[schemas.Post])
def read_user_posts(username: str, skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    user = db.query(models.User).filter(models.User.username ==
                                        username).offset(skip).limit(limit).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist."
        )

    return user.posts
