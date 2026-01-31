from twilio.rest import Client
from src.services.base import BaseService
from src.core.exceptions import MessagingError


class MessagingService(BaseService):
    """Service for sending messages via Twilio WhatsApp."""

    def __init__(self, settings):
        super().__init__(settings)
        self._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    async def send_whatsapp(self, to: str, body: str) -> str:
        """Send a WhatsApp message."""
        try:
            message = self._client.messages.create(
                from_=f"whatsapp:{self.settings.TWILIO_WHATSAPP_NUMBER}",
                to=to,
                body=body,
            )
            return message.sid
        except Exception as e:
            raise MessagingError(f"Failed to send message: {e}") from e
