from pydantic import BaseModel, EmailStr, validator, Field
from typing import List


class UserMail(BaseModel):
    email: EmailStr


class BaseUser(UserMail):
    name: str


class UserCreate(BaseUser):
    password: str
    verify_password: str

    @validator("password", "verify_password")
    def check_length(cls, v):
        if len(v) > 128:
            raise ValueError("Too many characters")
        return v

    @validator("verify_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v


class UserInfo(BaseUser):
    is_active: bool
    is_admin: bool


class UserInfoRoles(UserInfo):
    roles: List = Field(..., description="User roles")

    @validator("roles", pre=True)
    def to_list(cls, v):
        return [role_v.name for role_v in v]

    class Config:
        orm_mode = True


class UserInDB(UserInfo):
    id: int

    class Config:
        orm_mode = True


class UserWithRoles(BaseModel):
    id: int
    roles: List[str] = Field(..., description="User roles")
