from sqlalchemy.ext.asyncio import AsyncSession
from user.model import User
from user import repository
from user.schema import UserSelfAuthenticationRequest
from auth.security import verify_password, hash_password

class DeleteUserException(Exception):
    pass

async def delete_this(request: UserSelfAuthenticationRequest, db: AsyncSession, user: User) -> None:
    try:
        if not verify_password(request.password, user.hashed_pwd):
            raise DeleteUserException("Wrong password. Cannot delete this user.")
        await repository.delete_this(db, user)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise DeleteUserException("User deletion failed") from e