"""

Conversation Model

- TextContent: A class representing text content.
- CodeContent: A class representing code content.
- ImageContent: A class representing image content.
- MultimodalTextContent: A class representing multimodal text content.
- ExecutionOutputContent: A class representing execution output content.
- Author: A class representing the author of a message.
- Message: A class representing a message in a conversation.
- SimpleMessage: A class representing a simplified version of a message.
- Mapping: A class representing the mapping of messages in a conversation.
- Conversation: A class representing a conversation.

"""

from .conversation_model import Conversation
from .conversation_model import Mapping
from .conversation_model import Message

__all__ = [
    "Conversation",
    "Mapping",
    "Message",
]
