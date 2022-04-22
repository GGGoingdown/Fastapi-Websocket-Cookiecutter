from fastapi import APIRouter, Depends, status, HTTPException, Query, Security
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from dependency_injector.wiring import inject, Provide
from tortoise.transactions import atomic

# Application
from app import services, exceptions
from app.security import get_current_user_in_cache
from app.constants.error_codes import ERROR_CODES
from app.constants.roles import RoleEnum
from app.constants.responses import GET_USER_4XX_RESPONSES
from app.containers import Application
from app.schemas import GenericSchema, AuthSchema, UserSchema


auth_router = APIRouter(prefix="/auth", tags=["Authentication and Authorization"])


@auth_router.post(
    "/login",
    response_model=AuthSchema.LoginResponse,
    responses={
        401: {
            "model": GenericSchema.DetailResponse,
            "description": "Incorrect username or password",
        },
        403: {
            "model": GenericSchema.DetailResponse,
            "description": "Inactive account",
        },
    },
)
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    authenticate_service: services.AuthenticationService = Depends(
        Provide[Application.services.authentication_service]
    ),
    authorization_service: services.AuthorizationService = Depends(
        Provide[Application.services.authorization_service]
    ),
    user_service: services.UserService = Depends(
        Provide[Application.services.user_service]
    ),
    user_role_service: services.UserRoleService = Depends(
        Provide[Application.services.user_role_service]
    ),
):
    current_user = await authenticate_service.authenticate_user(
        email=form_data.username, password=form_data.password
    )
    logger.debug(f"[Login]::User - {current_user}")

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive account"
        )

    roles = await user_role_service.get_roles_by_user_id(current_user.id)

    logger.debug(f"[Login]::Roles: {roles}")

    access_token: str = authorization_service.create_jwt_token(
        user_id=current_user.id, scopes=roles
    )

    try:
        await user_service.save_user_in_cache(current_user.id)
    except exceptions.SaveError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error code: {ERROR_CODES.SAVE_CACHE_ERROR.code}",
        )

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post(
    "/sign-in",
    response_model=AuthSchema.SigninResponse,
    responses={
        409: {
            "model": GenericSchema.DetailResponse,
            "description": "Duplicate email",
        },
    },
)
@inject
@atomic()
async def sign_in(
    payload: UserSchema.UserCreate,
    user_service: services.UserService = Depends(
        Provide[Application.services.user_service]
    ),
    user_role_service: services.UserRoleService = Depends(
        Provide[Application.services.user_role_service]
    ),
    authenticate_service: services.AuthenticationService = Depends(
        Provide[Application.services.authentication_service]
    ),
    authorization_service: services.AuthorizationService = Depends(
        Provide[Application.services.authorization_service]
    ),
):
    try:

        quest_role_model = await user_role_service.get_role_by_name(RoleEnum.GUEST)
        password_hash = authenticate_service.get_password_hash(
            password=payload.password
        )
        user_model = await user_service.create_user(
            user_payload=payload,
            password_hash=password_hash,
            role_model=quest_role_model,
        )

        token = await authorization_service.save_active_token_in_cache(user_model.id)

    except exceptions.SaveDBUserError as e:
        logger.warning(e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Duplicate email"
        )

    except exceptions.RoleNotFoundError as e:
        logger.warning(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error code: {ERROR_CODES.NOT_FOUND_ERROR.code}",
        )

    except exceptions.CacheTokenError as e:
        logger.warning(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error code: {ERROR_CODES.SAVE_CACHE_ERROR.code}",
        )
    return {"active_token": token}


@auth_router.get(
    "/activate-user",
    response_model=GenericSchema.DetailResponse,
    responses={
        404: {
            "model": GenericSchema.DetailResponse,
            "description": "Not found",
        },
    },
)
@inject
@atomic()
async def activate_user(
    t: str = Query(..., description="active token"),
    authenticate_service: services.AuthenticationService = Depends(
        Provide[Application.services.authentication_service]
    ),
    user_service: services.UserService = Depends(
        Provide[Application.services.user_service]
    ),
):
    try:
        user_id = await authenticate_service.authenticate_active_token(t)
        await user_service.activate_user(user_id)

    except exceptions.NotFoundError:  # token was expried or invalid token
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    except exceptions.UpdateError as e:  # Activate user fail in db
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error code: {ERROR_CODES.UPDATE_ERROR.code}",
        )

    else:
        # Revoke token
        await authenticate_service.revoke_active_token(t)

    return {"detail": "activate user success"}


@auth_router.put(
    "/user-role",
    response_model=GenericSchema.DetailResponse,
    responses={
        **GET_USER_4XX_RESPONSES,
        404: {
            "model": GenericSchema.DetailResponse,
            "description": "Not found",
        },
    },
    dependencies=[Security(get_current_user_in_cache, scopes=[RoleEnum.SUPER_ADMIN])],
)
@inject
@atomic()
async def update_user_role(
    payload: UserSchema.UserMail,
    user_service: services.UserService = Depends(
        Provide[Application.services.user_service]
    ),
    user_role_service: services.UserRoleService = Depends(
        Provide[Application.services.user_role_service]
    ),
):
    if (user_model := await user_service.get_user_by_email(payload.email)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    try:
        admin_role_model = await user_role_service.get_role_by_name(RoleEnum.ADMIN)
        await user_service.add_user_role(user_model, [admin_role_model])

    except exceptions.NotFoundError as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error code: {ERROR_CODES.NOT_FOUND_ERROR.code}",
        )

    else:
        await user_service.remove_user_in_cache(user_model.id)

    return {"detail": "Update user permission success"}
