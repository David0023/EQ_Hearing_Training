from pydantic import BaseModel, ConfigDict, Field, EmailStr
from datetime import datetime

from user import validators

class UserBaseModel(BaseModel):
    username: str
    email: str

class UserCreateRequest(BaseModel):
    username: str = Field(
        min_length=validators.MIN_USERNAME_LENGTH,
        max_length=validators.MAX_USERNAME_LENGTH,
        pattern=validators.USERNAME_PATTERN
    )
    email: EmailStr
    password: str = Field(
        min_length=validators.MIN_PASSWORD_LENGTH,
        max_length=validators.MAX_PASSWORD_LENGTH,
    )

class UserCreateResponse(UserBaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class UserProfileResponse(UserBaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    profile_img_key: str | None

class UserSelfAuthenticationRequest(BaseModel):
    password: str

class UserProfileImageUploadResponse(BaseModel):
    profile_image_key: str