from pydantic_settings import BaseSettings
from urllib.parse import urlparse
from functools import lru_cache


class Settings(BaseSettings):
    # Twilio
    TWILIO_WHATSAPP_NUMBER: str
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str

    # OpenAI
    OPENAI_API_KEY: str

    # Redis (Fly.io provides this automatically, or use local Redis)
    REDIS_URL: str = "redis://localhost:6379"

    @property
    def redis_host(self) -> str:
        parsed = urlparse(self.REDIS_URL)
        return parsed.hostname or "localhost"

    @property
    def redis_port(self) -> int:
        parsed = urlparse(self.REDIS_URL)
        return parsed.port or 6379

    @property
    def redis_password(self) -> str | None:
        parsed = urlparse(self.REDIS_URL)
        return parsed.password

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
