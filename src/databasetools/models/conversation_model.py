from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel


class MessageContent(BaseModel):
    parts: List[Dict[str, str]]


class Author(BaseModel):
    role: str


class Message(BaseModel):
    id: str
    create_time: int
    update_time: int
    status: str
    end_turn: bool
    metadata: Dict[str, Any]
    recipient: str
    author: Author
    content: MessageContent


class Mapping(BaseModel):
    id: str
    parent: Optional[str]
    children: List[str]
    message: Message


class Conversation(BaseModel):
    id: str
    conversation_id: str
    conversation_template_id: str
    gizmo_id: str
    title: str
    create_time: int
    update_time: int
    mapping: Dict[str, Mapping]
    moderation_results: Optional[List[Any]]
    current_node: Optional[str]
    plugin_ids: Optional[List[str]]
    message_set: Optional[List[Dict[str, Any]]] = None
    summary: Optional[str] = None
