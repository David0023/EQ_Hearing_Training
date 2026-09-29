from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth.security import hash_password, verify_password, create_access_token, credentials_exception
from user import repository
from user.model import User
from user.schema import UserCreateRequest
from user.validators import check_email


async def register(db: AsyncSession, user_data: UserCreateRequest) -> User:
    is_valid_email, normalised_email = check_email(user_data.email)
    if not is_valid_email:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid Email: {normalised_email}"
                )

    if await repository.get_one(db, User.email==normalised_email):
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Existing Email"
                )
    try:
        new_user = await repository.create(
            db=db,
            username=user_data.username,
            email=normalised_email,
            hashed_pwd=hash_password(user_data.password)
        )
        return new_user
    except repository.UserCreationException as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user"
        ) from e


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
