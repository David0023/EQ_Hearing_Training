from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User

class UserCreationException(Exception):
    pass

async def get_one(db: AsyncSession, *conditions) -> User | None:
    query = select(User).where(*conditions).order_by(User.id.asc())
    result = await db.execute(query)
    return result.scalar_one_or_none()

# Assuming all inputs are valid.
async def create(db: AsyncSession, email: str, username: str, hashed_pwd: str) -> User:
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