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

    TRANSLATION_SYSTEM_PROMPT = (
        "You are a professional translator specializing in Chinese (Mandarin) to English translation, "
        "with expertise in Singaporean context including Singlish and code-switched content. "
        "Translate the given text to natural, fluent English. Preserve the original meaning and tone. "
        "For Singlish terms, provide the English equivalent in context."
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
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    prompt=self.LANGUAGE_PROMPT,
                )
            return response.text
        except Exception as e:
            raise TranscriptionError(f"Failed to transcribe: {e}") from e

    async def translate_to_english(self, file_path: str) -> str:
        """
        Two-step translation: transcribe with gpt-4o-transcribe, then translate to English with GPT-4o-mini.
        This ensures accurate transcription and reliable English translation.
        """
        try:
            # Step 1: Transcribe audio (preserves original language with high accuracy)
            with open(file_path, "rb") as audio_file:
                transcription_response = self._client.audio.transcriptions.create(
                    model="gpt-4o-transcribe",
                    file=audio_file,
                    prompt=self.LANGUAGE_PROMPT,
                )
            original_text = transcription_response.text

            # Step 2: Translate to English using GPT-4o-mini
            translation_response = self._client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": self.TRANSLATION_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"Translate this to English: {original_text}",
                    },
                ],
            )
            return translation_response.choices[0].message.content
        except Exception as e:
            raise TranscriptionError(f"Failed to translate: {e}") from e
