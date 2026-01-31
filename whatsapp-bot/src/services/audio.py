import httpx
import subprocess
import tempfile
import os
from src.services.base import BaseService
from src.core.exceptions import AudioDownloadError, AudioConversionError


class AudioService(BaseService):
    """Service for downloading and converting audio files."""

    async def download(self, media_url: str) -> str:
        """Download audio from Twilio with authentication."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    media_url,
                    auth=(
                        self.settings.TWILIO_ACCOUNT_SID,
                        self.settings.TWILIO_AUTH_TOKEN,
                    ),
                    follow_redirects=True,  # Follow Twilio's 307 redirect to CDN
                )
                response.raise_for_status()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as f:
                    f.write(response.content)
                    return f.name
        except Exception as e:
            raise AudioDownloadError(f"Failed to download audio: {e}") from e

    def convert_to_mp3(self, input_path: str) -> str:
        """Convert audio to mp3 using ffmpeg (Whisper-friendly format)."""
        try:
            output_path = input_path.replace(".ogg", ".mp3")
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    input_path,
                    "-acodec",
                    "libmp3lame",
                    "-y",
                    output_path,
                ],
                check=True,
                capture_output=True,
            )
            return output_path
        except subprocess.CalledProcessError as e:
            raise AudioConversionError(f"Failed to convert audio: {e}") from e

    @staticmethod
    def cleanup(*paths: str):
        """Delete temporary files."""
        for path in paths:
            if path and os.path.exists(path):
                os.remove(path)
