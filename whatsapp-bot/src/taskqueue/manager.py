import uuid
from typing import Optional

from kew import TaskQueueManager, QueueConfig, QueuePriority
from src.core.logging import logger
from src.config import get_settings
from src.core.dependencies import init_services


class AudioQueueManager:
    """Wrapper around Kew TaskQueueManager for audio processing tasks."""

    def __init__(self):
        self._manager: Optional[TaskQueueManager] = None
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return

        settings = get_settings()

        # Build Redis URL
        if settings.redis_password:
            redis_url = f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/0"
        else:
            redis_url = f"redis://{settings.redis_host}:{settings.redis_port}/0"

        self._manager = TaskQueueManager(redis_url=redis_url, cleanup_on_start=False)
        await self._manager.initialize()

        # Initialize services (needed by task functions)
        init_services(settings)

        # Create audio processing queue
        await self._manager.create_queue(
            QueueConfig(
                name="audio_processing",
                max_workers=5,
                max_size=100,
                priority=QueuePriority.MEDIUM,
                task_timeout=300,  # 5 minute timeout per task
                max_circuit_breaker_failures=5,
            )
        )

        self._initialized = True
        logger.info("Kew queue manager initialized")

    async def submit_audio_task(self, media_url: str, from_number: str) -> str:
        """Submit an audio processing task to the queue.

        Args:
            media_url: Twilio media URL for the audio file
            from_number: WhatsApp phone number of the sender

        Returns:
            The task ID
        """
        if not self._initialized:
            await self.initialize()

        # Generate unique task ID
        task_id = f"audio-{uuid.uuid4().hex[:8]}"

        # Submit task with the process_audio function
        await self._manager.submit_task(
            task_id=task_id,
            queue_name="audio_processing",
            task_type="process_audio",
            task_func=process_audio,
            priority=QueuePriority.MEDIUM,
            media_url=media_url,
            from_number=from_number,
        )

        logger.info(f"Submitted task {task_id} for audio processing")
        return task_id

    async def shutdown(self):
        if self._manager:
            await self._manager.shutdown(wait=True, timeout=10.0)
            self._initialized = False
            logger.info("Kew queue manager shut down")


# Global instance
_queue_manager: Optional[AudioQueueManager] = None


def get_queue_manager() -> AudioQueueManager:
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = AudioQueueManager()
    return _queue_manager


# Export for convenience
queue_manager = get_queue_manager()


async def process_audio(media_url: str, from_number: str):
    """
    Background task: download, transcribe, and reply.
    Called by Kew worker when a new task is dequeued.
    """
    from src.core.dependencies import get_services
    from src.core.exceptions import AppException

    services = get_services()
    input_path = None
    output_path = None

    try:
        # 1. Download from Twilio
        logger.info(f"Downloading from {media_url}")
        input_path = await services.audio.download(media_url)

        # 2. Convert to Whisper-friendly format
        logger.info(f"Converting {input_path} to MP3")
        output_path = services.audio.convert_to_mp3(input_path)

        # 3. Translate to English
        logger.info(f"Translating {output_path} to English")
        text = await services.transcription.translate(
            output_path, language_to="English"
        )

        if not text or text.strip() == "":
            text = "I couldn't hear anything in that audio."

        # 4. Send result back
        logger.info(f"Sending translation to {from_number}")
        await services.messaging.send_whatsapp(
            to=from_number, body=f"📝 Translation:\n\n{text}"
        )
        logger.info("Done!")

    except AppException as e:
        logger.error(f"AppException: {e}")
        await services.messaging.send_whatsapp(
            to=from_number,
            body="❌ Sorry, I couldn't transcribe that audio. Please try again.",
        )
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await services.messaging.send_whatsapp(
            to=from_number, body="❌ Something went wrong. Please try again later."
        )
        raise

    finally:
        services.audio.cleanup(input_path, output_path)
        logger.debug("Cleaned up temp files")
