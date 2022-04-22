from pydantic import BaseModel, Field
from typing import List


class JWTPayload(BaseModel):
    sub: str
    scopes: List[str]


class JWTTokenData(BaseModel):
    user_id: int
    scopes: List[str] = Field(..., description="User Policy")


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class SigninResponse(BaseModel):
    active_token: str
