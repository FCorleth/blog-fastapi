from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models


async def get_posts_repo(db: AsyncSession) -> list[models.Post]:
    posts = (
        await db.execute(
            select(models.Post).options(selectinload(models.Post.author))
        )
    ).scalars().all()
    return list(posts)


async def get_post_by_id_repo(post_id: int, db: AsyncSession) -> models.Post | None:
    post = (
        await db.execute(
            select(models.Post)
            .where(models.Post.id == post_id)
            .options(selectinload(models.Post.author))
        )
    ).scalars().first()
    return post


async def get_posts_by_user_id_repo(user_id: int, db: AsyncSession) -> list[models.Post]:
    posts = (
        await db.execute(
            select(models.Post)
            .where(models.Post.user_id == user_id)
            .options(selectinload(models.Post.author))
        )
    ).scalars().all()
    return list(posts)


async def create_post_repo(
    title: str, content: str, user_id: int, db: AsyncSession
) -> models.Post:
    post = models.Post(
        title=title,
        content=content,
        user_id=user_id,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


async def save_post_repo(post: models.Post, db: AsyncSession) -> models.Post:
    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


async def delete_post_repo(post: models.Post, db: AsyncSession) -> None:
    await db.delete(post)
    await db.commit()
