from sqlalchemy.ext.asyncio import AsyncSession

from repositories.users import (
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    create_user as create_user_repo, save_user,
    delete_user as delete_user_repo,
)

from repositories.posts import get_posts_by_user_id

import models
from schemas import UserUpdate
from services.exceptions import ConflictError, NotFoundError

async def get_user(user_id: int, db: AsyncSession) -> models.User:
    user = await get_user_by_id(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    return user


async def create_user(
    username: str, email: str, db: AsyncSession
) -> models.User:
    existing_user = await get_user_by_username(username, db)

    if existing_user:
        raise ConflictError("Username already exists")
    
    existing_email = await get_user_by_email(email, db)

    if existing_email:
        raise ConflictError("Email already exists")

    new_user = await create_user_repo(username, email, db)

    return new_user

async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession):
    user = await get_user_by_id(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    if user_data.username:
        username_already_exist = await get_user_by_username(user_data.username, db)

        if username_already_exist and username_already_exist.id != user_id:
            raise ConflictError("Username already exists")

        user.username = user_data.username
        
    if user_data.email:
        email_already_exist = await get_user_by_email(user_data.email, db)

        if email_already_exist and email_already_exist.id != user_id:
            raise ConflictError("Email already exists")
        
        user.email = user_data.email

    if user_data.image_file:
        user.image_file = user_data.image_file

    return await save_user(user, db)

async def delete_user(user_id: int, db: AsyncSession) -> None:
    user = await get_user_by_id(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    await delete_user_repo(user, db)

async def get_user_posts(user_id: int, db: AsyncSession) -> list[models.Post]:
    user = await get_user_by_id(user_id, db)

    if not user:
        raise NotFoundError("User not found")
    
    existing_posts = await get_posts_by_user_id(user_id, db)

    if not existing_posts:
        raise NotFoundError("Posts not found")

    return existing_posts

