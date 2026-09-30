from sqlalchemy.ext.asyncio import AsyncSession
from user.model import User
from user import repository

class DeleteUserException(Exception):
    pass

async def delete_this(db: AsyncSession, user: User) -> None:
    try:
        await repository.delete_this(db, user)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise DeleteUserException("User deletion failed") from e