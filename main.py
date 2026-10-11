from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, status, Depends
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from schemas import PostCreate, PostResponse, PostUpdate, UserResponse, UserCreate, UserUpdate

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import Base, engine, get_db

@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

@app.get("/api/posts", response_model=list[PostResponse])
async def get_posts(db:Annotated[AsyncSession, Depends(get_db)]):
    posts = (
        await db.execute(
            select(models.Post).options(selectinload(models.Post.author))
        )
    ).scalars().all()
    return posts

@app.get("/api/post/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    post = (
        await db.execute(
            select(models.Post)
            .where(models.Post.id == post_id)
            .options(selectinload(models.Post.author))
        )
    ).scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post

@app.put("/api/posts/{post_id}", response_model=PostResponse)
async def update_post_full(post_id: int, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    post = (
        await db.execute(
            select(models.Post)
            .where(models.Post.id == post_id)
            .options(selectinload(models.Post.author))
        )
    ).scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post_data.user_id != post.user_id:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User ID is diferent"
        )

    post.title = post_data.title
    post.content = post_data.title
    post.user_id = post_data.user_id

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    
    return post

@app.patch("/api/posts/{post_id}", response_model=PostResponse)
async def update_post_partial(post_id: int, post_data: PostUpdate, db:Annotated[AsyncSession,Depends(get_db)]):
    post = (
        await db.execute(
            select(models.Post)
            .where(models.Post.id == post_id)
            .options(selectinload(models.Post.author))
        )
    ).scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
  
    await db.commit()
    await db.refresh(post, attribute_names=["author"])

    return post

@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    post = (
        await db.execute(select(models.Post).where(models.Post.id == post_id))
    ).scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    await db.delete(post)
    await db.commit()
    
@app.get("/api/users/{user_id}", response_model=UserResponse, status_code=HTTP_200_OK)
async def get_user(user_id:int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = (
        await db.execute(select(models.User).where(models.User.id == user_id))
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing_user = (
        await db.execute(select(models.User).where(models.User.username == user.username))
    ).scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    existing_email = (
        await db.execute(select(models.User).where(models.User.email == user.email))
    ).scalars().first()

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
    await db.commit()
    await db.refresh(new_user)

    return new_user

@app.patch("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    user = (
        await db.execute(select(models.User).where(models.User.id == user_id))
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    if user_data.username:
        username_already_exist = (
            await db.execute(
                select(models.User).where(
                    models.User.username == user_data.username,
                    models.User.id != user_id
                )
            )
        ).scalars().first()

        if username_already_exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        user.username = user_data.username

    if user_data.email:
        email_already_exist = (
            await db.execute(
                select(models.User).where(
                    models.User.email == user_data.email,
                    models.User.id != user_id
                )
            )
        ).scalars().first()

        if email_already_exist:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        user.email = user_data.email
    
    if user_data.image_file:
        user.image_file = user_data.image_file

    await db.commit()

    return user

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = (
        await db.execute(select(models.User).where(models.User.id == user_id))
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await db.delete(user)
    await db.commit()

@app.get("/api/users/{user_id}/post", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = (
        await db.execute(select(models.User).where(models.User.id == user_id))
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    existing_posts = (
        await db.execute(
            select(models.Post)
            .where(models.Post.user_id == user_id)
            .options(selectinload(models.Post.author))
        )
    ).scalars().all()

    if not existing_posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Posts not found"
        )

    return existing_posts

@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    user = (
        await db.execute(select(models.User).where(models.User.id == post.user_id))
    ).scalars().first()
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
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])

    return new_post
