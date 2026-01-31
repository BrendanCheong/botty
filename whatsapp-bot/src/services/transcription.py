from openai import OpenAI
from src.services.base import BaseService
from src.core.exceptions import TranscriptionError


class TranscriptionService(BaseService):
    """Service for audio transcription using OpenAI Whisper."""

    # Language detection prompt - helps Whisper identify Chinese vs English
    LANGUAGE_PROMPT = (
        "This audio is in either Chinese (Mandarin) or English. "
        "Transcribe exactly what is spoken in the original language."
    )

    def __init__(self, settings):
        super().__init__(settings)
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, file_path: str) -> str:
        """
        Transcribe audio using Whisper with language detection.
        Supports Chinese (zh) and English (en).
        """
        try:
            with open(file_path, "rb") as audio_file:
                response = self._client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt=self.LANGUAGE_PROMPT,
                )
            return response.text
        except Exception as e:
            raise TranscriptionError(f"Failed to transcribe: {e}") from e

    async def translate_to_english(self, file_path: str) -> str:
        """
        Translate audio to English using Whisper.
        Use this if you want English output regardless of input language.
        """
        try:
            with open(file_path, "rb") as audio_file:
                response = self._client.audio.translations.create(
                    model="whisper-1", file=audio_file
                )
            return response.text
        except Exception as e:
            raise TranscriptionError(f"Failed to translate: {e}") from e
