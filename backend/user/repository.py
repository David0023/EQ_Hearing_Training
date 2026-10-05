from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from user.model import User

async def get_one(db: AsyncSession, *conditions) -> User | None:
    """Return the first user matching the SQLAlchemy conditions."""
    query = select(User).where(*conditions).order_by(User.id.asc())
    result = await db.execute(query)
    return result.scalar_one_or_none()

# Assuming all inputs are valid.
async def create(
    db: AsyncSession,
    email: str,
    username: str,
    hashed_pwd: str,
    flush: bool = False,
) -> User:
    """Persist and return a user.

    Raises:
        UserCreationException: If persisting the user fails.
    """
    new_user = User(
        email=email,
        username=username,
        hashed_pwd=hashed_pwd
    )
    db.add(new_user)
    if flush:
        await db.flush()
        await db.refresh(new_user)
    return new_user

async def update(
    db: AsyncSession,
    user: User,
    flush: bool = False,
    **kwargs
) -> User:
    """Update and return a user.

    Raises:
        ValueError: If an unsupported field is provided.
    """
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

    for field, value in kwargs.items():
        setattr(user, field, value)
    if flush:
        await db.flush()
        await db.refresh(user)
    return user

async def delete_this(
    db: AsyncSession,
    user: User | None,
    flush: bool = False,
) -> bool:
    if user is None:
        return False
    await db.delete(user)
    if flush:
        await db.flush()
    return True