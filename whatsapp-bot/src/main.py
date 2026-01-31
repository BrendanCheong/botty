from robyn import Robyn

from src.config import get_settings
from src.core.logging import logger
from src.routes import health, webhook
from src.taskqueue.manager import queue_manager


app = Robyn(__file__)


# Include routers
app.include_router(health.router)
app.include_router(webhook.router)


@app.startup_handler
async def startup():
    """Initialize services and Kew queue manager on startup."""
    settings = get_settings()

    logger.info("Initializing services...")

    # Initialize Kew queue manager (this also initializes services)
    logger.info(f"Connecting to Redis at {settings.redis_host}:{settings.redis_port}")
    await queue_manager.initialize()

    logger.info("Ready!")


@app.shutdown_handler
async def shutdown():
    """Clean up on shutdown."""
    logger.info("Shutting down...")
    await queue_manager.shutdown()


if __name__ == "__main__":
    app.start(host="0.0.0.0", port=8080)
