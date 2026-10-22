from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from auth.dependencies import get_current_user
from db.database import get_db
from user import service
from user.model import User
from user.schema import (
    UserProfileResponse,
    UserSelfAuthenticationRequest,
    UserProfileImageUploadResponse
)

from storage.images import service as img_service
from core.config import settings


# Keep the existing public URLs while separating account routes from authentication.
router = APIRouter(prefix="/users", tags=["user"])

@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserProfileResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Return the authenticated user."""
    return current_user

@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    background_tasks: BackgroundTasks,
    request: UserSelfAuthenticationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete the authenticated user."""
    img_key = current_user.profile_img_key
    try:
        await service.delete_user(request, db, current_user)
    except service.UserUnauthenticated as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not delete user",
            )
    finally:
        if img_key is not None:
            background_tasks.add_task(img_service.delete_image, settings.LOCAL_UPLOAD_DIR, current_user.img_key)


@router.put('/profile/image', 
    status_code=status.HTTP_200_OK,
    response_model=UserProfileImageUploadResponse,
)
async def update_profile(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = await service.update_profile_image(db, current_user, file)
        if result.obsolete_image_key is not None:
            background_tasks.add_task(img_service.delete_image, settings.LOCAL_UPLOAD_DIR, result.obsolete_image_key)
        return UserProfileImageUploadResponse(profile_image_key=result.profile_image_key)
    except service.ProfileImageInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not upload image"
        )
    finally:
        await file.close()