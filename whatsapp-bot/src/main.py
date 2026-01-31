from robyn import Robyn
from arq import create_pool
from arq.connections import RedisSettings

from src.config import get_settings
from src.core.dependencies import init_services
from src.core.logging import logger
from src.routes import health, webhook


app = Robyn(__file__)


# Include routers
app.include_router(health.router)
app.include_router(webhook.router)


@app.startup_handler
async def startup():
    """Initialize services and Redis connection on startup."""
    settings = get_settings()

    logger.info("Initializing services...")

    # Initialize service container
    init_services(settings)

    # Create Redis pool for job queue
    logger.info(f"Connecting to Redis at {settings.redis_host}:{settings.redis_port}")
    redis_pool = await create_pool(
        RedisSettings(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
        )
    )

    # Inject into webhook router
    webhook.set_redis_pool(redis_pool)

    logger.info("Ready!")


@app.shutdown_handler
async def shutdown():
    """Clean up on shutdown."""
    logger.info("Shutting down...")


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=8080)
