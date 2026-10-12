from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

from services.exceptions import ConflictError, NotFoundError
from services.users import (
    get_user as get_user_service,
    create_user as create_user_service,
    update_user as update_user_service,
    delete_user as delete_user_service,
    get_user_posts as get_user_posts_service,
)

from schemas import PostResponse, UserCreate, UserResponse, UserUpdate

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await create_user_service(user.username, user.email, db)
    except ConflictError as exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exception.detail
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await get_user_service(user_id, db)
    except NotFoundError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.detail,
        )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, user_data: UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    try:
        return await update_user_service(user_id, user_data, db)
    except NotFoundError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.detail
        )
    except ConflictError as exception:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exception.detail
        )



@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await delete_user_service(user_id, db)
    except NotFoundError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.detail,
        )

@router.get("/{user_id}/post", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await get_user_posts_service(user_id, db)
    except NotFoundError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.detail,
        )
