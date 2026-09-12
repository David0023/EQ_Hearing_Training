from pydantic import BaseModel, ConfigDict
from datetime import datetime

class UserCreateRequest(BaseModel):
    username: str
    password: str

class UserCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    created_at: datetime
    updated_at: datetime
