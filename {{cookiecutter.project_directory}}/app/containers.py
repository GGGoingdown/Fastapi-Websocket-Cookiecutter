# Build-in
from dependency_injector import containers, providers

# Application
from app import repositories, services, db


class Gateways(containers.DeclarativeContainer):
    config = providers.Configuration()
    redis_client = providers.Resource(db.redis_init)

    # DB resource
    db_resource = providers.Resource(db.DBResource, connect_config=db.TORTOISE_ORM)

    # # SocketIO
    socketio_client = providers.Resource(db.socketio_init)


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()
    gateways = providers.DependenciesContainer()

    # Initial Resource
    jwt_manager = providers.Resource(
        services.JWTManager,
        jwt_secret_key=config.jwt.secret_key,
        jwt_algorithm=config.jwt.algorithm,
        jwt_expired_time_minute=config.jwt.expire_min,
    )

    token_selector = providers.Resource(services.TokenSelector, jwt=jwt_manager)

    # * Repositories *#
    user_repo = providers.Singleton(repositories.UserRepo)

    user_role_repo = providers.Singleton(repositories.UserRoleRepo)

    # * Cache *#
    user_cache = providers.Singleton(
        repositories.UserCache,
        redis_client=gateways.redis_client,
        expired_time_min=config.jwt.expire_min,
    )

    auth_cache = providers.Singleton(
        repositories.AuthCache,
        redis_client=gateways.redis_client,
    )

    # * Services *#
    user_service = providers.Singleton(
        services.UserService,
        user_repo=user_repo,
        user_role_repo=user_role_repo,
        user_cache=user_cache,
    )

    user_role_service = providers.Singleton(
        services.UserRoleService,
        user_role_repo=user_role_repo,
    )

    authentication_service = providers.Singleton(
        services.AuthenticationService,
        user_repo=user_repo,
        auth_cache=auth_cache,
        token_selector=token_selector,
    )

    authorization_service = providers.Singleton(
        services.AuthorizationService,
        auth_cache=auth_cache,
        token_selector=token_selector,
    )

    # * Websocket *#
    task_websocket_manager = providers.Singleton(services.TaskWebsocketManager)

    # * SocketIO *#
    task_socketio_manager = providers.Singleton(
        services.TaskSocketioManager, socketio_client=gateways.socketio_client
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()
    gateways = providers.Container(Gateways, config=config)
    services = providers.Container(Services, config=config, gateways=gateways)
