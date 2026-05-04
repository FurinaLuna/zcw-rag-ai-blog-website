from datetime import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=50)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminInfo(BaseModel):
    id: int
    username: str
    created_at: datetime
    last_login_at: datetime | None = None

    model_config = {"from_attributes": True}
