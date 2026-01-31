from src.core.dependencies import get_services
from src.core.exceptions import AppException
from src.core.logging import logger


async def process_audio(ctx, media_url: str, from_number: str):
    """
    Main background job: download, transcribe, and reply.
    Called by arq worker when a new job is dequeued.
    """
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

        # 3. Transcribe with Whisper (auto-detects Chinese/English)
        logger.info(f"Transcribing {output_path}")
        text = await services.transcription.transcribe(output_path)

        if not text or text.strip() == "":
            text = "I couldn't hear anything in that audio."

        # 4. Send result back
        logger.info(f"Sending transcription to {from_number}")
        await services.messaging.send_whatsapp(
            to=from_number, body=f"📝 Transcription:\n\n{text}"
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
