from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from schemas import PostCreate, PostResponse, UserResponse, UserCreate

from sqlalchemy import select
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db:Annotated[Session, Depends(get_db)]):
    posts = db.execute(select(models.Post)).scalars().all()
    return posts

@app.get("/api/post/{post_id}", response_model=PostResponse)
def get_post(req: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):

    post = db.execute(select(models.Post).where(models.Post.id == post_id)).scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post
   
@app.get("/api/users/{user_id}", response_model=UserResponse, status_code=HTTP_200_OK)
def get_user(user_id:int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

@app.post("/api/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    username_result = db.execute(select(models.User).where(models.User.username == user.username))
    existing_user = username_result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    email_result = db.execute(select(models.User).where(models.User.email == user.email))
    existing_email = email_result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.get("/api/users/{user_id}/post", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(models.User).where(models.User.id == user_id)).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    post_result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    existing_posts = post_result.scalars().all()

    if not existing_posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posts not found"
        )

    return existing_posts

@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(select(models.User).where(models.User.id == post.user_id)).scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post
    
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(req: Request, exception: StarletteHTTPException):
    message = ( exception.detail if exception.detail else "An error occurred. Pleash check your request and try again." )
    
    if req.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message}
        )

    return templates.TemplateResponse(
        req,
        "error.html",
        {
            "status_code": exception.status_code,
            "title":exception.status_code ,
            "message": message
        },
        status_code=exception.status_code
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(req: Request, exception: RequestValidationError):
    if req.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exception.errors()}
        )
    
    return templates.TemplateResponse(
        req,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title":status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your request and try again."
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )
