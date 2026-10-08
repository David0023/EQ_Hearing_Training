from pydantic import BaseModel, Field

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=512)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str
