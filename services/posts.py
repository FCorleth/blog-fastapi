from sqlalchemy.ext.asyncio import AsyncSession

from repositories import posts, users

import models
from schemas import PostCreate, PostUpdate
from services.exceptions import ForbiddenError, NotFoundError


async def get_posts_service(db: AsyncSession) -> list[models.Post]:
    return await posts.get_posts_repo(db)


async def get_post_service(post_id: int, db: AsyncSession) -> models.Post:
    post = await posts.get_post_by_id_repo(post_id, db)

    if not post:
        raise NotFoundError("Post not found")

    return post


async def create_post_service(
    title: str, content: str, user_id: int, db: AsyncSession
) -> models.Post:
    user = await users.get_user_by_id_repo(user_id, db)

    if not user:
        raise NotFoundError("User not found")

    return await posts.create_post_repo(title, content, user_id, db)


async def update_post_full_service(
    post_id: int, post_data: PostCreate, user_id: int, db: AsyncSession
) -> models.Post:
    post = await posts.get_post_by_id_repo(post_id, db)

    if not post:
        raise NotFoundError("Post not found")

    if post.user_id != user_id:
        raise ForbiddenError("Not allowed to update this post")

    post.title = post_data.title
    post.content = post_data.content

    return await posts.save_post_repo(post, db)


async def update_post_partial_service(
    post_id: int, post_data: PostUpdate, user_id: int, db: AsyncSession
) -> models.Post:
    post = await posts.get_post_by_id_repo(post_id, db)

    if not post:
        raise NotFoundError("Post not found")

    if post.user_id != user_id:
        raise ForbiddenError("Not allowed to update this post")

    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    return await posts.save_post_repo(post, db)


async def delete_post_service(post_id: int, user_id: int, db: AsyncSession) -> None:
    post = await posts.get_post_by_id_repo(post_id, db)

    if not post:
        raise NotFoundError("Post not found")

    if post.user_id != user_id:
        raise ForbiddenError("Not allowed to delete this post")

    await posts.delete_post_repo(post, db)
