from urllib.parse import parse_qs
from robyn import SubRouter, Request
from src.core.logging import logger


router = SubRouter(__name__, prefix="")


@router.post("/webhook")
async def webhook(request: Request):
    """
    Twilio webhook endpoint for incoming WhatsApp messages.

    Quickly acknowledges the webhook and enqueues the audio processing job.
    This prevents Twilio from timing out on longer audio files.
    """
    # Import queue_manager here to avoid circular imports
    from src.taskqueue.manager import queue_manager

    form_data = parse_qs(request.body, keep_blank_values=True)
    form_data = {k: v[0] if v else "" for k, v in form_data.items()}

    from_number = form_data.get("From", "")
    num_media = int(form_data.get("NumMedia", "0"))

    logger.info(f"Received message from {from_number}, NumMedia={num_media}")

    if num_media > 0:
        media_url = form_data.get("MediaUrl0", "")
        media_type = form_data.get("MediaContentType0", "")

        # Only process audio files
        if media_type.startswith("audio/"):
            logger.info("Enqueueing job for audio processing")
            await queue_manager.submit_audio_task(media_url, from_number)
        else:
            logger.info(f"Skipping non-audio media: {media_type}")

    return {"status": "ok"}
