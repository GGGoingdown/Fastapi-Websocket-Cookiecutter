import traceback
from tortoise import Tortoise, run_async
from tenacity import retry, stop_after_attempt, wait_fixed
from loguru import logger

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(stop=stop_after_attempt(max_tries), wait=wait_fixed(wait_seconds))
async def db_connecttion():
    try:
        # Application
        from app.containers import Application

        container = Application()

        logger.info("--- Connect DB ---")
        await container.gateways.db_resource.init()
        conn = Tortoise.get_connection("default")
        logger.info(f"Ping -> {await conn.execute_query('SELECT 1')}")

    except ConnectionRefusedError as e:
        error_message = traceback.format_exc()
        logger.error(error_message)
        raise e

    except Exception as e:
        error_message = traceback.format_exc()
        logger.error(error_message)
        raise e

    finally:
        await container.gateways.db_resource.shutdown()


@retry(stop=stop_after_attempt(max_tries), wait=wait_fixed(wait_seconds))
def broker_connecttion():
    # Application
    from app.main import celery

    try:

        logger.info("--- Connect Broker ---")
        celery.broker_connection().ensure_connection(max_retries=3)
    except Exception as e:
        error_message = traceback.format_exc()
        logger.error(error_message)
        raise e


async def main():
    logger.info("--- Initial services ---")
    await db_connecttion()
    broker_connecttion()
    logger.info("--- Initial services successful ---")


if __name__ == "__main__":
    run_async(main())
