from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User

class UserCreationException(Exception):
    pass

async def get_one(db: AsyncSession, *conditions) -> User | None:
    query = select(User).where(*conditions).order_by(User.id.asc())
    result = await db.execute(query)
    return result.scalar_one_or_none()

# Assuming all inputs are valid.
async def create(
    db: AsyncSession,
    email: str,
    username: str,
    hashed_pwd: str
) -> User:
    new_user = User(
        email=email,
        username=username,
        hashed_pwd=hashed_pwd
    )
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        db.session.rollback()
        raise UserCreationException(e)

async def update(
    db: AsyncSession,
    user: User,
    **kwargs
) -> User:
    allowed_fields = {
        "username",
        "email",
        "hashed_pwd",
    }
    invalid_fields = set(kwargs) - allowed_fields

    if invalid_fields:
        raise ValueError(
            f"Cannot update fields: {', '.join(sorted(invalid_fields))}"
        )

    try:
        for field, value in kwargs.items():
            setattr(user, field, value)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise e

async def delete_one(
    db: AsyncSession,
    *conditions
) -> int:
    query = select(User).where(*conditions).order_by(User.id.asc())
    result = await db.execute(query)
    user = result.scalars().first()
    if user is None:
        return 0

    try:
        await db.delete(user)
        await db.commit()
        return 1
    except Exception as e:
        await db.rollback()
        raise e

async def delete_many(
    db: AsyncSession,
    *conditions
) -> int:
    query = delete(User).where(*conditions)
    try:
        result = await db.execute(query)
        await db.commit()
        return result.rowcount or 0
    except Exception as e:
        await db.rollback()
        raise e