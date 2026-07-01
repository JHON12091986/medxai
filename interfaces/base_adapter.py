import abc
from typing import Any, Dict, Optional

class BaseChannelAdapter(abc.ABC):
    """Abstract base class for all OmniBridge external communication channel adapters."""

    @abc.abstractmethod
    async def send_message(self, chat_id: str, text: str, parse_mode: Optional[str] = None) -> Any:
        """Send a standard text message to the channel."""
        pass

    @abc.abstractmethod
    async def receive_message(self, message_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming message payload received from the channel."""
        pass
