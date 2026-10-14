from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from repositories import posts, users

import models
from schemas import Token, UserUpdate
from services.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError

from auth import (
    create_access_token,
    hash_password,
    verify_access_token,
    verify_password
)


async def login_service(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    user = await users.get_user_by_username_repo(form_data.username, db)

    if not user or not verify_password(form_data.password, user.password_hash):
        raise UnauthorizedError("User unauthorized")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


async def get_current_user_service(token: str, db: AsyncSession):
    user_id = verify_access_token(token)

    if user_id is None:
        raise UnauthorizedError("User unauthorized")

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedError("User unauthorized")

    user = await users.get_user_by_id_repo(user_id_int, db)

    if user is None:
        raise UnauthorizedError("User unauthorized")

    return user


async def get_user_service(user_id: int, db: AsyncSession) -> models.User:
    user = await users.get_user_by_id_repo(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    return user


async def create_user_service(
    username: str, email: str, password: str, db: AsyncSession
) -> models.User:
    existing_user = await users.get_user_by_username_repo(username, db)

    if existing_user:
        raise ConflictError("Username already exists")

    existing_email = await users.get_user_by_email_repo(email, db)

    if existing_email:
        raise ConflictError("Email already exists")

    hashed_password = hash_password(password)

    new_user = await users.create_user_repo(username, email, hashed_password, db)

    return new_user


async def update_user_service(
    user_id: int,
    user_data: UserUpdate,
    current_user: models.User,
    db: AsyncSession,
) -> models.User:
    user = await users.get_user_by_id_repo(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    if user.id != current_user.id:
        raise ForbiddenError("Not authorized to update this user")

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


async def delete_user_service(user_id: int, current_user: models.User, db: AsyncSession) -> None:
    user = await users.get_user_by_id_repo(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    if user.id != current_user.id:
        raise ForbiddenError("Not authorized to delete this user")

    await users.delete_user_repo(user, db)


async def get_user_posts_service(user_id: int, db: AsyncSession) -> list[models.Post]:
    user = await users.get_user_by_id_repo(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    existing_posts = await posts.get_posts_by_user_id_repo(user_id, db)

    if not existing_posts:
        raise NotFoundError("Posts not found")

    return existing_posts
