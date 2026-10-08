import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from auth import service
from auth.schema import LoginResponse, RefreshTokenRequest, TokenRefreshResponse
from db.database import get_db
from user.schema import UserCreateRequest, UserCreateResponse
from user.model import User
from auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreateRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await service.register(db, user_data)
    except service.InvalidEmail as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except service.DuplicateEmail as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception:
        logger.exception("Registration failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user",
        )

@router.post("/login", status_code=status.HTTP_200_OK, response_model=LoginResponse)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    try:
        return await service.login(db, form_data.username, form_data.password)
    except service.InvalidLoginInfo as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
        logger.exception("Login failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login Failed")

@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenRefreshResponse)
async def refresh(
    request: RefreshTokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    try:
        return await service.refresh(db, request.refresh_token)
    except service.InvalidRefreshToken as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
        logger.exception("Refresh failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Refresh Failed")

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        await service.revoke_refresh_token(db, request.refresh_token, user.id)
    except service.InvalidRefreshToken as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
        logger.exception("Logout failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")
