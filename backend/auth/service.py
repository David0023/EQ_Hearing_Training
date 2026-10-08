from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from auth import security
from user import repository as user_repo
from user.model import User
from user.schema import UserCreateRequest
from user.validators import check_email
from auth.refresh_token import service as refresh_token_service

class InvalidLoginInfo(Exception):
    pass

class InvalidRefreshToken(Exception):
    pass

class InvalidEmail(Exception):
    pass

class DuplicateEmail(Exception):
    pass

class RefreshTokenCreationFailed(Exception):
    pass

MAX_REFRESH_TOKEN_ATTEMPTS = 3

async def _store_refresh_token(
    db: AsyncSession,
    user_id: int,
) -> security.RefreshTokenInfo:
    refresh_token = security.generate_refresh_token()
    await refresh_token_service.create(
        db,
        user_id=user_id,
        token_hash=refresh_token.token_hash,
        expires_at=refresh_token.expires_at,
    )
    return refresh_token

async def _store_refresh_token_with_retry(
    db: AsyncSession,
    user_id: int,
) -> security.RefreshTokenInfo:
    for attempt in range(MAX_REFRESH_TOKEN_ATTEMPTS):
        try:
            # Isolate a rare unique-hash collision without rolling back the
            # surrounding login/refresh transaction or its row locks.
            async with db.begin_nested():
                refresh_token = await _store_refresh_token(db, user_id)
            return refresh_token
        except refresh_token_service.TokenDuplicate as exc:
            if attempt + 1 == MAX_REFRESH_TOKEN_ATTEMPTS:
                raise RefreshTokenCreationFailed(
                    "Could not create a unique refresh token"
                ) from exc
    raise RefreshTokenCreationFailed("Could not create a refresh token")

def is_email_unique_violation(exc: IntegrityError) -> bool:
    original = exc.orig
    constraint_name = getattr(original, "constraint_name", None)

    if constraint_name is None:
        diag = getattr(original, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None)

    if constraint_name == "uq_users_email":
        return True

    # PostgreSQL drivers do not all expose constraint_name on the same object.
    # The server error message still includes the named constraint.
    original_message = str(original)
    return (
        '"uq_users_email"' in original_message
        or "UNIQUE constraint failed: users.email" in original_message
    )

async def register(db: AsyncSession, user_data: UserCreateRequest) -> User:
    is_valid_email, normalised_email = check_email(user_data.email)
    if not is_valid_email:
        raise InvalidEmail(f"Invalid Email: {normalised_email}")

    if await user_repo.get_one(db, User.email==normalised_email):
        raise DuplicateEmail("Existing Email")
    try:
        new_user = await user_repo.create(
            db=db,
            username=user_data.username,
            email=normalised_email,
            hashed_pwd=security.hash_password(user_data.password),
            flush=True
        )

        await db.commit()
        return new_user
    except IntegrityError as exc:
        await db.rollback()
        if is_email_unique_violation(exc):
            raise DuplicateEmail("Existing Email") from exc
        raise
    except Exception:
        # Any unknown errors.
        await db.rollback()
        raise

        
async def login(db: AsyncSession, email: str, password: str) -> dict[str, str]:
    async with db.begin():
        # Login via email
        existing_user = await user_repo.get_one(db, User.email==email)
        if not existing_user or not security.verify_password(password, existing_user.hashed_pwd):
            raise InvalidLoginInfo("Incorrect email and/or password")
    
        access_token = security.create_access_token(existing_user.id, role="user")
        refresh_token = await _store_refresh_token_with_retry(db, existing_user.id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token.raw_token
        }

async def revoke_refresh_token(db: AsyncSession, raw_token: str, user_id: int) -> None:
    try:
        token = await refresh_token_service.get_valid(
            db, security.hash_refresh_token(raw_token), user_id=user_id
        )
        await refresh_token_service.revoke(db, token)
        await db.commit()
    except (refresh_token_service.TokenRevoked,
            refresh_token_service.TokenNotFound,
            refresh_token_service.TokenExpired):
        await db.rollback()
        raise InvalidRefreshToken("Invalid Refresh Token")
    except Exception:
        await db.rollback()
        raise

async def refresh(db: AsyncSession, raw_token: str) -> dict[str, str]:
    try:
        old_token = await refresh_token_service.get_valid(
            db, security.hash_refresh_token(raw_token)
        )
        access_token = security.create_access_token(old_token.user_id, role="user")
        new_refresh_token = await _store_refresh_token_with_retry(db, old_token.user_id)
        await refresh_token_service.revoke(db, old_token)
        await db.commit()
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": new_refresh_token.raw_token,
        }
    except (refresh_token_service.TokenRevoked,
            refresh_token_service.TokenNotFound,
            refresh_token_service.TokenExpired) as exc:
        await db.rollback()
        raise InvalidRefreshToken("Invalid Refresh Token") from exc
    except Exception:
        await db.rollback()
        raise
