from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models

async def get_user_by_id(user_id: int, db: AsyncSession) -> models.User | None:
    user = (
        await db.execute(select(models.User).where(models.User.id == user_id))
    ).scalars().first()

    return user

async def get_user_by_username(username: str, db: AsyncSession) -> models.User | None:
    user = (
        await db.execute(select(models.User).where(models.User.username == username))
    ).scalars().first()

    return user

async def get_user_by_email(email: str, db: AsyncSession) -> models.User | None:
    user = (
        await db.execute(select(models.User).where(models.User.email == email))
    ).scalars().first()

    return user

async def create_user(username: str, email: str, db: AsyncSession) -> models.User:
    user = models.User(
        username=username,
        email=email,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user

async def save_user(user: models.User, db: AsyncSession) -> models.User:
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(user: models.User, db: AsyncSession) -> None:
    await db.delete(user)
    await db.commit()