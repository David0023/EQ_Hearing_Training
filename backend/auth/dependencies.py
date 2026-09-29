from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession


from db.database import get_db
from auth.security import decode_token, credentials_exception
from user.model import User
from user.repository import get_one

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
