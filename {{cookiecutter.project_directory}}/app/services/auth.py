from fastapi import HTTPException, status
from fastapi.security import SecurityScopes
from typing import Dict, Iterable
from jose import JWTError, jwt
from passlib.context import CryptContext
from loguru import logger
from datetime import datetime, timedelta

# Application
from app import repositories, utils, exceptions
from app.schemas import UserSchema, AuthSchema


class JWTManager:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    __slots__ = (
        "_jwt_secret_key",
        "_jwt_algorithm",
        "_jwt_expired_time_minute",
    )

    def __init__(
        self,
        jwt_secret_key: str,
        jwt_algorithm: str,
        jwt_expired_time_minute: int = 120,
    ) -> None:
        self._jwt_secret_key = jwt_secret_key
        self._jwt_algorithm = jwt_algorithm
        self._jwt_expired_time_minute = jwt_expired_time_minute

    def decode(self, token: str) -> Dict:
        try:
            payload = jwt.decode(
                token,
                self._jwt_secret_key,
                algorithms=[self._jwt_algorithm],
                options={"verify_aud": False},
            )

            return payload

        except JWTError:
            raise self.credentials_exception

    def encode(self, payload: Dict) -> str:
        encoded_jwt = jwt.encode(
            payload, self._jwt_secret_key, algorithm=self._jwt_algorithm
        )
        return encoded_jwt

    def create_expired_time(self) -> datetime:
        expried_dt = utils.get_utc_now() + timedelta(
            minutes=self._jwt_expired_time_minute
        )
        return expried_dt


class TokenSelector:
    def __init__(self, jwt: JWTManager) -> None:
        self.jwt = jwt


class BaseAuthService:
    invalid_username_or_password_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def _verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)


class AuthenticationService(BaseAuthService):
    __slots__ = ("_user_repo", "_token_selector", "_auth_cache")

    def __init__(
        self,
        user_repo: repositories.UserRepo,
        token_selector: TokenSelector,
        auth_cache: repositories.AuthCache,
    ) -> None:
        self._user_repo = user_repo
        self._token_selector = token_selector
        self._auth_cache = auth_cache

    async def authenticate_user(self, email: str, password: str) -> UserSchema.UserInDB:
        if (user := await self._user_repo.get_by_mail(email)) is None:
            logger.info("Invalid e-mail")
            raise self.invalid_username_or_password_exception

        if not self._verify_password(password, user.password_hash):
            logger.info("Invalid password")
            raise self.invalid_username_or_password_exception

        return UserSchema.UserInDB.from_orm(user)

    async def authenticate_active_token(self, token: str) -> int:
        if user_id := await self._auth_cache.get_active_token(token):
            return user_id
        raise exceptions.ActiveTokenNotFoundError()

    async def revoke_active_token(self, token: str):
        res = await self._auth_cache.delete_active_token(token)
        return res

    async def authenticate_jwt(
        self, security_scopes: SecurityScopes, token: str
    ) -> UserSchema.UserWithRoles:
        # Decode JWT
        payload = self._token_selector.jwt.decode(token)
        # Get User ID
        if (user_id := payload.get("sub")) is None:
            raise self._token_selector.jwt.credentials_exception
        # Get Roles
        user_scopes = payload.get("scopes", [])
        AuthSchema.JWTTokenData(user_id=user_id, scopes=user_scopes)

        if security_scopes.scopes:
            authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        else:
            authenticate_value = "Bearer"

        for scope in security_scopes.scopes:
            if scope not in user_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )

        return UserSchema.UserWithRoles(id=user_id, roles=user_scopes)


class AuthorizationService(BaseAuthService):
    __slots__ = ("_token_selector", "_auth_cache")

    def __init__(
        self,
        token_selector: TokenSelector,
        auth_cache: repositories.AuthCache,
    ) -> None:
        self._token_selector = token_selector
        self._auth_cache = auth_cache

    def create_jwt_token(self, *, user_id: int, scopes: Iterable[str]) -> str:
        payload = AuthSchema.JWTPayload(sub=user_id, scopes=scopes).dict()
        expried_dt = self._token_selector.jwt.create_expired_time()
        payload.update({"exp": expried_dt})
        return self._token_selector.jwt.encode(payload)

    async def save_active_token_in_cache(self, user_id: int) -> str:
        state, token = await self._auth_cache.save_active_token(user_id)
        if not state:
            raise exceptions.CacheTokenError(state)
        return token
