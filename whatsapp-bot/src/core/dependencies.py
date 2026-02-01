from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from src.config import Settings, get_settings
from src.services.audio import AudioService
from src.services.transcription import TranscriptionService
from src.services.messaging import MessagingService

if TYPE_CHECKING:
    from src.taskqueue.manager import AudioQueueManager


@dataclass
class ServiceContainer:
    """Container holding all service instances."""

    audio: AudioService
    transcription: TranscriptionService
    messaging: MessagingService
    queue_manager: "AudioQueueManager | None" = field(default=None)


def create_services(settings: Settings | None = None) -> ServiceContainer:
    """Factory function to create all services with injected settings."""
    if settings is None:
        settings = get_settings()

    return ServiceContainer(
        audio=AudioService(settings),
        transcription=TranscriptionService(settings),
        messaging=MessagingService(settings),
    )


# Global container (initialized at startup)
_container: ServiceContainer | None = None


def get_services() -> ServiceContainer:
    """Get the global service container."""
    global _container
    if _container is None:
        _container = create_services()
    return _container


def init_services(settings: Settings | None = None):
    """Initialize the global service container."""
    global _container
    _container = create_services(settings)


def set_queue_manager(queue_manager: "AudioQueueManager"):
    """Set the queue manager in the global container."""
    global _container
    if _container is None:
        _container = create_services()
    _container.queue_manager = queue_manager
