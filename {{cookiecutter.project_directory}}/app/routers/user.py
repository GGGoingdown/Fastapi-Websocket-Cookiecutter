from typing import List
from fastapi import APIRouter, Depends, Query, Security
from dependency_injector.wiring import inject, Provide

# Application
from app import services
from app.containers import Application
from app.schemas import UserSchema, GenericSchema
from app.security import get_current_user_in_cache
from app.constants import RoleEnum, GET_USER_4XX_RESPONSES

user_router = APIRouter(prefix="/users", tags=["User"])


@user_router.get(
    "",
    dependencies=[Security(get_current_user_in_cache, scopes=[RoleEnum.SUPER_ADMIN])],
    response_model=List[UserSchema.UserInfo],
    responses={**GET_USER_4XX_RESPONSES},
)
@inject
async def get_all_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, gt=0, le=100),
    user_service: services.UserService = Depends(
        Provide[Application.services.user_service]
    ),
):
    users = await user_service.get_all_users(offset=offset, limit=limit)
    return users


@user_router.get(
    "/me",
    response_model=UserSchema.UserInfoRoles,
    responses={
        401: {
            "model": GenericSchema.DetailResponse,
            "description": "Could not validate credentials",
        },
    },
)
@inject
async def get_me(
    current_user: UserSchema.UserWithRoles = Depends(get_current_user_in_cache),
    user_service: services.UserService = Depends(
        Provide[Application.services.user_service]
    ),
):
    user = await user_service.get_user_with_roles(current_user.id)
    return user
