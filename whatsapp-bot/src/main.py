from robyn import Robyn

from src.config import get_settings
from src.core.logging import logger
from src.core.dependencies import set_queue_manager
from src.routes import health, webhook
from src.taskqueue.manager import get_queue_manager


app = Robyn(__file__)


# Include routers
app.include_router(health.router)
app.include_router(webhook.router)


@app.startup_handler
async def startup():
    """Initialize services and Kew queue manager on startup."""
    settings = get_settings()

    logger.info("Initializing services...")

    logger.info(f"Connecting to Redis at {settings.redis_host}:{settings.redis_port}")
    queue_manager = get_queue_manager()
    await queue_manager.initialize()

    # Register queue_manager in the service container
    set_queue_manager(queue_manager)

    logger.info("Ready!")


@app.shutdown_handler
async def shutdown():
    """Clean up on shutdown."""
    logger.info("Shutting down...")
    queue_manager = get_queue_manager()
    await queue_manager.shutdown()


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=8080)
