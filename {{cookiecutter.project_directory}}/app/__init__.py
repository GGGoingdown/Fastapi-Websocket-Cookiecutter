import sys
import sentry_sdk
import socketio
from socketio.asyncio_pubsub_manager import AsyncPubSubManager
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from fastapi import FastAPI
from fastapi.routing import APIRoute
from loguru import logger
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from sentry_sdk._types import Event, Hint

# Application
from app.config import settings, EnvironmentMode, LogLevel
from app.utils import logger_init

# Initial logger
if settings.app.env_mode == EnvironmentMode.PROD:
    # Production Mode
    logger_init(LogLevel.WARNING)
else:
    logger_init(LogLevel.DEUBG)


__VERSION__ = "0.0.1"


def create_socketio(
    app: FastAPI, socketio_client: AsyncPubSubManager
) -> socketio.AsyncServer:
    if settings.app.env_mode == EnvironmentMode.PROD:
        logger = False
        engineio_logger = False
    else:
        logger = True
        engineio_logger = True

    sio = socketio.AsyncServer(
        async_mode="asgi",
        client_manager=socketio_client,
        logger=logger,
        engineio_logger=engineio_logger,
        cors_allowed_origins=settings.app.cors_allowed_origins,
    )

    # # * Register namespace * #
    from app.routers import TaskSocketIONamespace
    from app.constants.socketio_namespaces import NamespaceEnum

    sio.register_namespace(TaskSocketIONamespace(f"/{NamespaceEnum.task.value}"))

    asgi = socketio.ASGIApp(
        socketio_server=sio,
    )
    app.mount("/ws", asgi)


def create_app() -> FastAPI:
    app = FastAPI(
        servers=[
            {"url": "https://stag.example.com", "description": "Staging environment"},
            {
                "url": "https://prod.example.com",
                "description": "Production environment",
            },
        ],
        title="{{cookiecutter.project_name}}",
        version=__VERSION__,
        description="This project is create FastAPI Celery",
    )
    #! Must before add router
    from app.broker import create_celery

    app.celery_app = create_celery()

    if settings.sentry.dns:
        # Initial sentry and add middleware
        logger.info("--- Initial Sentry ---")
        sentry_sdk.init(
            settings.sentry.dns,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=settings.sentry.trace_sample_rates,
        )

        class CustomSentryAsgiMiddleware(SentryAsgiMiddleware):
            def event_processor(
                self, event: "Event", hint: "Hint", asgi_scope: Any
            ) -> "Optional[Event]":
                result_event = super().event_processor(event, hint, asgi_scope)
                route: Optional[APIRoute] = asgi_scope.get("route")
                if route and result_event:
                    result_event["transaction"] = route.path
                return result_event

        app.add_middleware(CustomSentryAsgiMiddleware)

    # Dependency injection
    from app.containers import Application

    container = Application()
    container.config.from_pydantic(settings)
    # Add routers
    from app import routers, security

    app.include_router(routers.health_router)
    app.include_router(routers.user_router)
    app.include_router(routers.auth_router)
    app.include_router(routers.ws_router)
    app.include_router(routers.view_router)
    app.include_router(routers.event_router)

    from app.broker import tasks

    # Mount container
    container.wire(
        modules=[
            sys.modules[__name__],
            routers.health,
            routers.user,
            routers.auth,
            routers.ws,
            routers.event,
            security,
            tasks,
        ]
    )
    app.container = container

    @app.on_event("startup")
    async def startup_event():
        logger.info("--- Startup Event ---")
        await app.container.services.init_resources()
        # * Socketio * #
        socketio_client = app.container.gateways.socketio_client()
        create_socketio(app, socketio_client=socketio_client)

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("--- Shutdown Event ---")
        await app.container.services.shutdown_resources()

    return app
