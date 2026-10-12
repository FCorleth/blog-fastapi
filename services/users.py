from sqlalchemy.ext.asyncio import AsyncSession

from repositories import posts, users

import models
from schemas import UserUpdate
from services.exceptions import ConflictError, NotFoundError


async def get_user_service(user_id: int, db: AsyncSession) -> models.User:
    user = await users.get_user_by_id_repo(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    return user


async def create_user_service(
    username: str, email: str, db: AsyncSession
) -> models.User:
    existing_user = await users.get_user_by_username_repo(username, db)

    if existing_user:
        raise ConflictError("Username already exists")

    existing_email = await users.get_user_by_email_repo(email, db)

    if existing_email:
        raise ConflictError("Email already exists")

    new_user = await users.create_user_repo(username, email, db)

    return new_user


async def update_user_service(
    user_id: int, user_data: UserUpdate, db: AsyncSession
) -> models.User:
    user = await users.get_user_by_id_repo(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    if user_data.username:
        username_already_exist = await users.get_user_by_username_repo(
            user_data.username, db
        )

        if username_already_exist and username_already_exist.id != user_id:
            raise ConflictError("Username already exists")

        user.username = user_data.username

    if user_data.email:
        email_already_exist = await users.get_user_by_email_repo(user_data.email, db)

        if email_already_exist and email_already_exist.id != user_id:
            raise ConflictError("Email already exists")

        user.email = user_data.email

    if user_data.image_file:
        user.image_file = user_data.image_file

    return await users.save_user_repo(user, db)


async def delete_user_service(user_id: int, db: AsyncSession) -> None:
    user = await users.get_user_by_id_repo(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    await users.delete_user_repo(user, db)


async def get_user_posts_service(user_id: int, db: AsyncSession) -> list[models.Post]:
    user = await users.get_user_by_id_repo(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    existing_posts = await posts.get_posts_by_user_id_repo(user_id, db)

    if not existing_posts:
        raise NotFoundError("Posts not found")

    return existing_posts
