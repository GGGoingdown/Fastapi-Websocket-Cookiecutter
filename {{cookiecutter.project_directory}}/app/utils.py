import sys
import shortuuid
from loguru import logger
from datetime import datetime

# Application
from app.config import LogLevel


def logger_init(log_level: LogLevel = LogLevel.DEUBG) -> None:
    logger.remove()
    logger.info("Initalize log formater ...")
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time}</green> |<y>[{level}]</y> | <e>{file}::{function}::{line}</e> | {message}",
        filter="",
        level=log_level.value,
    )


def get_utc_now() -> datetime:
    return datetime.utcnow().replace(microsecond=0)


def dt_to_string(dt: datetime):
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def get_shortuuid() -> str:
    return shortuuid.uuid()
