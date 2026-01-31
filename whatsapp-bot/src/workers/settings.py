from arq.connections import RedisSettings
from src.workers.tasks import process_audio
from src.config import get_settings

# Create Redis settings at module level for arq
_settings = get_settings()
redis_settings = RedisSettings(
    host=_settings.redis_host,
    port=_settings.redis_port,
    password=_settings.redis_password,
)


class WorkerSettings:
    """arq worker configuration."""

    functions = [process_audio]
    redis_settings = redis_settings
    max_jobs = 10
    job_timeout = 300  # 5 minutes max per job
