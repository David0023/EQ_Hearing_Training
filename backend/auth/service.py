from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from auth.security import hash_password, verify_password, create_access_token, credentials_exception
from user import repository
from user.model import User
from user.schema import UserCreateRequest
from user.validators import check_email

class UserCreationException(Exception):
    pass

class EmailAlreadyExists(Exception):
    pass

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
        raise UserCreationException(f"Invalid Email: {normalised_email}")

    if await repository.get_one(db, User.email==normalised_email):
        raise EmailAlreadyExists("Existing Email")
    try:
        new_user = await repository.create(
            db=db,
            username=user_data.username,
            email=normalised_email,
            hashed_pwd=hash_password(user_data.password),
            flush=True
        )

        await db.commit()
        return new_user
    except IntegrityError as exc:
        await db.rollback()
        if is_email_unique_violation(exc):
            raise EmailAlreadyExists("Existing Email") from exc
        raise
    except Exception as e:
        # Any unknown errors.
        await db.rollback()
        raise

        
async def login(db: AsyncSession, email: str, password: str) -> dict[str, str]:
    # Login via email
    existing_user = await repository.get_one(db, User.email==email)
    if not existing_user or not verify_password(password, existing_user.hashed_pwd):
        raise credentials_exception

    return {
        "access_token": create_access_token(
            user_id=existing_user.id,
            role="user"
        ),
        "token_type": "bearer"
    }
