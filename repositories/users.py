from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models


async def get_user_by_id_repo(user_id: int, db: AsyncSession) -> models.User | None:
    user = (
        await db.execute(select(models.User).where(models.User.id == user_id))
    ).scalars().first()

    return user


async def get_user_by_username_repo(username: str, db: AsyncSession) -> models.User | None:
    user = (
        await db.execute(select(models.User).where(models.User.username == username))
    ).scalars().first()

    return user


async def get_user_by_email_repo(email: str, db: AsyncSession) -> models.User | None:
    user = (
        await db.execute(select(models.User).where(models.User.email == email))
    ).scalars().first()

    return user


async def create_user_repo(username: str, email: str, db: AsyncSession) -> models.User:
    user = models.User(
        username=username,
        email=email,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def save_user_repo(user: models.User, db: AsyncSession) -> models.User:
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user_repo(user: models.User, db: AsyncSession) -> None:
    await db.delete(user)
    await db.commit()
