from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostResponse, UserCreate, UserResponse, UserUpdate

from repositories.users import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    create_user as create_user_repo,
    delete_user as delete_user_repo,
    save_user,
)

router = APIRouter()

@router.post("",response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing_user = await get_user_by_username(user.username, db)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    existing_email = await get_user_by_email(user.email, db)

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    new_user = await create_user_repo(user.username, user.email, db)

    return new_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id:int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    if user_data.username:
        username_already_exist = await get_user_by_username(user_data.username, db)

        if username_already_exist and username_already_exist.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )

        user.username = user_data.username

    if user_data.email:
        email_already_exist = await get_user_by_email(user_data.email, db)

        if email_already_exist and email_already_exist.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists"
            )

        user.email = user_data.email
    
    if user_data.image_file:
        user.image_file = user_data.image_file

    return await save_user(user, db)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_user_by_id(user_id, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await delete_user_repo(user, db)

@router.get("/{user_id}/post", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_user_by_id(user_id, db)

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