from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import AsyncGenerator


from core.database import SessionLocal
from core.security import decode_token, credentials_exception
from core.database import SessionLocal
from models.user import User
from repositories.user import get_one

# Dependency: Get D
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session and close it after use."""
    async with SessionLocal() as db:
        yield db

# set oauth2_schemce to Bearer token scheme (Token URL is for the Docs)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Authenticate 
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Return the user identified by the bearer token."""
    token_data = decode_token(token)
    user = await get_one(db, User.id==int(token_data.sub))
    if user is None:
        raise credentials_exception
    return user