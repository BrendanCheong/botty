class AppException(Exception):
    """Base exception for the application."""

    pass


class AudioDownloadError(AppException):
    """Failed to download audio from Twilio."""

    pass


class AudioConversionError(AppException):
    """Failed to convert audio format."""

    pass


class TranscriptionError(AppException):
    """Failed to transcribe audio."""

    pass


class MessagingError(AppException):
    """Failed to send message via Twilio."""

    pass
