from fastapi import APIRouter, Depends, HTTPException, status
from fastapi. security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from schemas.user import UserCreateRequest, UserCreateResponse
from core.dependencies import get_db
from core.security import hash_password, verify_password, create_access_token, credentials_exception
from repositories.user import create_user, get_one_user

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post('/register', response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    if await get_one_user(db, username=user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Existing Username"
        )

    try:
        new_user = await create_user(db, user_data.username, hash_password(user_data.password))
        return new_user
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e
        )

@router.post('/login', status_code=status.HTTP_200_OK)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    user = await get_one_user(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_pwd):
        raise credentials_exception

    return {
        "access_token": create_access_token(
            username=user.username,
            role="user"
        ),
        "token_type": "bearer"
    }