import jwt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, ValidationError
from fastapi import HTTPException, status
from pwdlib import PasswordHash

from core.config import settings

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

class TokenData(BaseModel):
    sub: str
    exp: int
    iat: int
    role: str

def create_access_token(
    user_id: int,
    role: str
) -> str:
    """Create a signed access token for a user and role."""
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    iat = datetime.now(timezone.utc)
    to_encode = {
        "sub": str(user_id),
        "role": role,
        "exp": int(exp.timestamp()),
        "iat": int(iat.timestamp())
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> TokenData:
    """Decode a token and return its validated token data.

    Raises:
        HTTPException: If the token is expired or cannot be validated.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenData(
            sub=str(payload["sub"]),
            exp=int(payload["exp"]),
            iat=int(payload["iat"]),
            role=payload["role"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception
    except ValidationError:
        raise credentials_exception

# Refresh Token
class RefreshTokenInfo(BaseModel):
    raw_token: str
    token_hash: str
    expires_at: datetime

def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(
        raw_token.encode()
    ).hexdigest()

def generate_refresh_token() -> RefreshTokenInfo:
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_refresh_token(raw_token)

    token = RefreshTokenInfo(
        raw_token=raw_token,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return token

# Password
# Define password hashing scheme
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check whether a plain-text password matches a stored hash."""
    return password_hash.verify(plain_password, hashed_password)
