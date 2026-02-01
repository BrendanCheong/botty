from openai import OpenAI
from src.services.base import BaseService
from src.core.exceptions import TranscriptionError


class TranscriptionService(BaseService):
    """Service for audio transcription using OpenAI Whisper."""

    LANGUAGE_PROMPT = (
        "This audio is in either Chinese (Mandarin) or English. "
        "Transcribe exactly what is spoken in the original language. "
        "Note that the audio may contain code-switching between Chinese and English, or they may be spoken with a Singaporean accent. "
        "Please accurately capture all spoken content. Make sure that Singlish terms and phrases are transcribed correctly."
    )

    def _get_translation_prompt(self, language_to: str) -> str:
        """Generate translation prompt for the target language."""
        return (
            f"You are a professional translator specializing in Chinese (Mandarin) to {language_to} translation, "
            f"with expertise in Singaporean context including Singlish and code-switched content. "
            f"Translate the given text to natural, fluent {language_to}. Preserve the original meaning and tone. "
            f"For Singlish terms, provide the {language_to} equivalent in context."
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
                transcription = self._client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    prompt=self.LANGUAGE_PROMPT,
                )
            return transcription.text
        except Exception as e:
            raise TranscriptionError(f"Failed to transcribe: {e}") from e

    async def translate(self, file_path: str, language_to: str = "English") -> str:
        """
        Translate audio directly to target language using gpt-4o-transcribe.

        Args:
            file_path: Path to the audio file
            language_to: Target language for translation (default: "English")

        Returns:
            Translated text in the target language
        """
        try:
            with open(file_path, "rb") as audio_file:
                translation_response = self._client.audio.translations.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    prompt=self._get_translation_prompt(language_to),
                )
            return translation_response.text
        except Exception as e:
            raise TranscriptionError(f"Failed to translate: {e}") from e
