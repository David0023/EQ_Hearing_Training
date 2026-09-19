from fastapi import APIRouter, Depends, HTTPException, status
from fastapi. security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from schemas.user import UserCreateRequest, UserCreateResponse, UserMeResponse
from core.dependencies import get_db, get_current_user
from core.security import hash_password, verify_password, create_access_token, credentials_exception
from repositories.user import (
    create as create_user, 
    get_one as get_one_user
)
from utils.validator import check_email
from models.user import User

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post('/register', response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    is_valid_email, normalised_email = check_email(user_data.email)
    if not is_valid_email:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid Email: {normalised_email}"
                )

    if await get_one_user(db, User.email==normalised_email):
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Existing Email"
                )
    try:
        new_user = await create_user(
            db=db, 
            username=user_data.username, 
            email=normalised_email, 
            hashed_pwd=hash_password(user_data.password)
        )
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
    # Login via email
    user = await get_one_user(db, User.email==form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_pwd):
        raise credentials_exception

    return {
        "access_token": create_access_token(
            user_id=user.id,
            role="user"
        ),
        "token_type": "bearer"
    }

@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserMeResponse)
async def me(
    current_user: User = Depends(get_current_user)
):
    return current_user