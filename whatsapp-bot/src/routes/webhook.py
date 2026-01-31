from robyn import SubRouter, Request
from src.core.logging import logger


router = SubRouter(__name__, prefix="")

# Redis pool reference (set by main.py)
_redis_pool = None


def set_redis_pool(pool):
    """Inject the Redis/arq pool into the webhook router."""
    global _redis_pool
    _redis_pool = pool


@router.post("/webhook")
async def webhook(request: Request):
    """
    Twilio webhook endpoint for incoming WhatsApp messages.

    Quickly acknowledges the webhook and enqueues the audio processing job.
    This prevents Twilio from timing out on longer audio files.
    """
    form_data = request.form_data

    from_number = form_data.get("From", "")
    num_media = int(form_data.get("NumMedia", "0"))

    logger.info(f"Received message from {from_number}, NumMedia={num_media}")

    if num_media > 0:
        media_url = form_data.get("MediaUrl0", "")
        media_type = form_data.get("MediaContentType0", "")

        # Only process audio files
        if media_type.startswith("audio/"):
            logger.info("Enqueueing job for audio processing")
            await _redis_pool.enqueue_job("process_audio", media_url, from_number)
        else:
            logger.info(f"Skipping non-audio media: {media_type}")

    # Always return 200 OK quickly to prevent Twilio timeout
    return {"status":"ok"}
