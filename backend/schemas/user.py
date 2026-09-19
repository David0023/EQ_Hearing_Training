from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserBaseModel(BaseModel):
    username: str
    email: str

class UserCreateRequest(UserBaseModel):
    password: str

class UserCreateResponse(UserBaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class UserMeResponse(UserBaseModel):
    id: int
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    