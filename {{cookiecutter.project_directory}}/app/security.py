from fastapi import Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

# Application
from app import services
from app.containers import Application
from app.schemas import UserSchema

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={},
)


@inject
async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    authenticate_service: services.AuthenticationService = Depends(
        Provide[Application.services.authentication_service]
    ),
) -> UserSchema.UserWithRoles:
    return await authenticate_service.authenticate_jwt(security_scopes, token=token)


@inject
async def get_current_user_in_cache(
    current_user: UserSchema.UserWithRoles = Depends(get_current_user),
    user_service: services.UserService = Depends(
        Provide[Application.services.user_service]
    ),
) -> UserSchema.UserWithRoles:
    if not await user_service.user_exists_in_cache(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials [cache]",
        )

    return current_user


@inject
async def get_admin(
    current_user: UserSchema.UserInDB = Depends(get_current_user),
) -> UserSchema.UserInDB:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
