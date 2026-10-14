from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth import CurrentUser
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate
from services import posts
from services.exceptions import ForbiddenError, NotFoundError

router = APIRouter()


@router.get("", response_model=list[PostResponse])
async def get_posts(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    return await posts.get_posts_service(current_user, db)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(current_user: CurrentUser, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await posts.get_post_service(post_id, current_user, db)
    except NotFoundError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.detail,
        )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(
    current_user: CurrentUser,
    post_id: int,
    post_data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        return await posts.update_post_full_service(
            post_id, post_data, current_user.id, db
        )
    except NotFoundError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.detail,
        )
    except ForbiddenError as exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exception.detail,
        )


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(
    current_user: CurrentUser,
    post_id: int,
    post_data: PostUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        return await posts.update_post_partial_service(
            post_id, post_data, current_user.id, db
        )
    except NotFoundError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.detail,
        )
    except ForbiddenError as exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exception.detail,
        )


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(current_user: CurrentUser, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await posts.delete_post_service(post_id, current_user.id, db)
    except NotFoundError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.detail,
        )
    except ForbiddenError as exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exception.detail,
        )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        return await posts.create_post_service(
            post.title, post.content, current_user.id, db
        )
    except NotFoundError as exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.detail,
        )
