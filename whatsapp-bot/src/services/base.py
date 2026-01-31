from abc import ABC
from src.config import Settings


class BaseService(ABC):
    """Base class for all services with shared dependencies."""

    def __init__(self, settings: Settings):
        self._settings = settings

    @property
    def settings(self) -> Settings:
        return self._settings
