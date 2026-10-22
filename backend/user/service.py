from dataclasses import dataclass
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from user.model import User
from user import repository
from user.schema import UserSelfAuthenticationRequest
from auth.security import verify_password
from core.config import settings
from storage.images import service as img_service

logger = logging.getLogger(__name__)

class UserUnauthenticated(Exception):
    pass

class ProfileImageInvalidError(Exception):
    """When Profile image is invalid image"""

@dataclass
class ProfileImageUpdateResult:
    profile_image_key: str
    obsolete_image_key: str | None

async def delete_user(request: UserSelfAuthenticationRequest, db: AsyncSession, user: User) -> None:
    try:
        if not verify_password(request.password, user.hashed_pwd):
            raise UserUnauthenticated("Wrong password.")
        await repository.delete_this(db, user)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

async def update_profile_image(db: AsyncSession, user: User, file: img_service.AsyncReadable) -> ProfileImageUpdateResult:
    image: img_service.ImageMetadata | None = None
    try:
        image = await img_service.upload_image(settings.LOCAL_UPLOAD_DIR, file)
        image_key = f"{image.id}{image.extension}"
        prev_profile = user.profile_img_key
    
        await repository.update(
            db, user, flush=True, 
            profile_img_key=image_key
        )
        await db.commit()
        return ProfileImageUpdateResult(profile_image_key=image_key, obsolete_image_key=prev_profile)
    except img_service.InvalidImageError as e:
        raise ProfileImageInvalidError(str(e))
    except Exception:
        await db.rollback()
        if image is not None:
            image_key = f"{image.id}{image.extension}"
            try:
                img_service.delete_image(settings.LOCAL_UPLOAD_DIR, image_key)
            except OSError:
                logger.exception(
                    "Failed to remove uploaded profile image %s",
                    image_key,
                )
        raise 