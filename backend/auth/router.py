import logging
from typing import Annotated
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from auth import service
from auth.schema import LoginResponse, TokenRefreshResponse
from db.database import get_db
from user.schema import UserCreateRequest, UserCreateResponse
from user.model import User
from auth.dependencies import get_current_user
from core.config import settings

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
    try:
        result = await service.login(db, form_data.username, form_data.password)
        access_token = result.access_token
        refresh_token = result.refresh_token
        response.set_cookie(
            key="refresh_token",
            value=refresh_token.raw_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            path="/auth",
            max_age=int((refresh_token.expires_at - refresh_token.created_at).total_seconds()),
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"

        return LoginResponse(
            access_token=access_token,
            token_type='bearer',
        )
    except service.InvalidLoginInfo as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
        logger.exception("Login failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login Failed")

@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenRefreshResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    try:
        if not refresh_token:
            raise service.InvalidRefreshToken("Missing refresh token")
        result = await service.refresh(db, refresh_token)
        new_refresh_token = result.refresh_token
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token.raw_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            path="/auth",
            max_age=int((new_refresh_token.expires_at - new_refresh_token.created_at).total_seconds()),
        )
        return TokenRefreshResponse(access_token=result.access_token)
    except service.InvalidRefreshToken as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
        logger.exception("Refresh failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Refresh Failed")

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        if refresh_token:
            await service.revoke_refresh_token(db, refresh_token, user.id)
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            path="/auth",
        )
    except service.InvalidRefreshToken as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
        logger.exception("Logout failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed")
