from sqlalchemy.ext.asyncio import AsyncSession
from user.model import User
from user import repository
from user.schema import UserSelfAuthenticationRequest
from auth.security import verify_password

class UserUnauthenticated(Exception):
    pass

async def delete_user(request: UserSelfAuthenticationRequest, db: AsyncSession, user: User) -> None:
    try:
        if not verify_password(request.password, user.hashed_pwd):
            raise UserUnauthenticated("Wrong password.")
        await repository.delete_this(db, user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise