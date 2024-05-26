"""Data Model for OpenAI Conversation

The data model for the OpenAI conversation is defined in this module. The data model includes the following classes:

- TextContent: A class representing text content.
- CodeContent: A class representing code content.
- ImageContent: A class representing image content.
- MultimodalTextContent: A class representing multimodal text content.
- ExecutionOutputContent: A class representing execution output content.

The data model also includes the following classes:

- Author: A class representing the author of a message.
- Message: A class representing a message in a conversation.
- SimpleMessage: A class representing a simplified version of a message.
- Mapping: A class representing the mapping of messages in a conversation.
- Conversation: A class representing a conversation.

The data model is used to define the structure of the data that is stored and processed in the OpenAI conversation.
"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import field_validator


class TextContent(BaseModel):
    content_type: str = "text"
    parts: List[str]

    def __str__(self):
        return " ".join(self.parts)


# {
#     "content_type": "code",
#     "language": "unknown",
#     "response_format_name": null,
#     "text": "import markdown"
# },
class CodeContent(BaseModel):
    content_type: str = "code"
    language: Optional[str] = "unknown"
    response_format_name: Optional[str] = None
    text: Optional[str] = None

    def __str__(self):
        return f"```{self.language}\n{self.text}\n```"


# {
#     "content_type": "image_asset_pointer",
#     "asset_pointer": "file-service://file-KzHN5YTeunrqqYrQLq1rNOdT",
#     "size_bytes": 172934,
#     "width": 1792,
#     "height": 1024,
#     "fovea": 512,
#     "metadata": {
#         "dalle": {
#             "gen_id": "TOnMHK4NTysIAmxQ",
#             "prompt": "A UI mockup for an app named 'FlowArchitect'. The interface features a modern and clean design with a focus on usability and functionality. The main layout includes a top navigation bar with menu items (Home, Viewpoints, Templates, Reports, Settings) and a user avatar, a left sidebar with node libraries and tools, a central canvas for designing flows with drag-and-drop functionality, a right sidebar for properties and configurations, and a bottom panel for output logs and console. The color scheme includes shades of blue and white, giving it a professional and technological feel.",
#             "seed": 2378848015,
#             "parent_gen_id": null,
#             "edit_op": null,
#             "serialization_title": "DALL-E generation metadata"
#         },
#         "sanitized": false
#     }
# }
class ImageContent(BaseModel):
    content_type: str = "image_asset_pointer"
    asset_pointer: str
    size_bytes: int
    width: int
    height: int
    metadata: Dict[str, Any]


# {
# "content_type": "multimodal_text",
# "parts": []
class MultimodalTextContent(BaseModel):
    content_type: str = "multimodal_text"
    parts: Optional[List[Dict[str, Any]]]


# "content_type": "execution_output",
# "text": "'/mnt/data/App_Design_Summary.md'"


class ExecutionOutputContent(BaseModel):
    content_type: str = "execution_output"
    text: Optional[str]

    def __str__(self):
        return self.text


ACCEPTABLE_CONTENT_TYPES = ["code", "execution_output", "text"]
REQUIRED_ATTRIBUTES = {
    "text": ["parts"],
    "code": ["language", "text"],
    "multimodal_text": ["parts"],
    "execution_output": ["text"],
}


def validate_content_type(content_type: str, content: Dict[str, Any]):
    if content_type not in ACCEPTABLE_CONTENT_TYPES:
        print(f"Invalid content type: {content_type} skipping validation")
        return
    if content_type in REQUIRED_ATTRIBUTES:
        for attr in REQUIRED_ATTRIBUTES[content_type]:
            if attr not in content:
                raise ValueError(f"Content type {content_type} requires attribute {attr} has {content}")


# {
#     "role": "user",
#     "name": null,
#     "metadata": {}
# },
class Author(BaseModel):
    role: str
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __str__(self):
        return self.role


# {
#     "id": "aaa23f00-9117-4700-85fd-e4be81fdf783",
#     "author": Author,
#     "create_time": 1716514617.117903,
#     "update_time": null,
#     "content": Content
#     "status": "finished_successfully",
#     "end_turn": null,
#     "weight": 1.0,
#     "metadata": {
#         "request_id": "88898ec28ec62ac1-LAX",
#         "message_source": null,
#         "timestamp_": "absolute",
#         "message_type": null
#     },
#     "recipient": "all"
# },


class Message(BaseModel):
    id: str
    author: Author
    create_time: Optional[float]
    update_time: Optional[float]
    status: str
    end_turn: Optional[bool]
    recipient: str
    weight: float
    metadata: Dict[str, Any]

    content: Union[TextContent, CodeContent, MultimodalTextContent]

    @field_validator("content")
    def validate_content(cls, value):
        validate_content_type(value.content_type, value.model_dump())
        return value

    def __str__(self):
        return f"[{self.author.role}, {self.weight}]: {self.content:20}"


class SimpleMessage(BaseModel):
    role: str
    content: str

    def __str__(self):
        return f"{self.role}: {self.content:20}..."

    @classmethod
    def from_message(cls, message: Message) -> "SimpleMessage":
        if message is None:
            return cls(role="unknown", content="")
        content = str(message.content) if message.content is not None else ""
        role = message.author.role if message.author is not None else "unknown"
        return cls(role=role, content=content)


# {
# "aaa23f00-9117-4700-85fd-e4be81fdf783": {
# "id": "aaa23f00-9117-4700-85fd-e4be81fdf783",
# "message": Message
# "parent": "920fce9e-8cd0-4483-9ca5-f2f2f6123331",
# "children": [
#     "2e882f7e-6250-41e8-a591-c740f36a2696"
# ]
# },
# "2e882f7e-6250-41e8-a591-c740f36a2696": {
# "id": "2e882f7e-6250-41e8-a591-c740f36a2696",
# "message": Message,
# "parent": "aaa23f00-9117-4700-85fd-e4be81fdf783",
# "children": [
#     "e82cb0b0-9f61-41d8-b7ca-32cb887bddb6"
# ]
# },
# "e82cb0b0-9f61-41d8-b7ca-32cb887bddb6": {
# "id": "e82cb0b0-9f61-41d8-b7ca-32cb887bddb6",
# "message": Message,
# "parent": "2e882f7e-6250-41e8-a591-c740f36a2696",
# "children": []
# }
# },
class Mapping(BaseModel):
    id: str
    parent: Optional[str]
    children: Optional[List[str]]
    message: Optional[Message]

    def __str__(self):
        return f"[{self.parent:5}]{self.id:5} -> {self.message:20}..."


# {
# "conversation_id": "9bb26374-a22f-4158-923f-5b66f80aa885",
# "conversation_template_id": null,
# "create_time": 1716514617.111505,
# "current_node": "e82cb0b0-9f61-41d8-b7ca-32cb887bddb6",
# "default_model_slug": "gpt-4",
# "gizmo_id": null,
# "id": "9bb26374-a22f-4158-923f-5b66f80aa885"
# "is_archived": false,
# "moderation_results": [],
# "plugin_ids": null,
# "safe_urls": [],
# "title": "Avoid Conversion Char Star",
# "update_time": 1716514648.140268,
# },
class Conversation(BaseModel):
    id: str
    conversation_id: str
    title: Optional[str] = "No Title"
    conversation_template_id: Optional[str] = None
    default_model_slug: Optional[str] = "gpt-unk"
    gizmo_id: Optional[str] = None
    create_time: float
    update_time: float
    current_node: Optional[str]
    moderation_results: Optional[List[Any]]
    plugin_ids: Optional[List[str]] = None
    safe_urls: Optional[List[str]] = None
    mapping: Dict[str, Mapping]

    def __str__(self):
        return f"[{self.default_model_slug}]: {self.title} -- {self.id:10}"

    def to_records(self) -> List[SimpleMessage]:
        records = []
        for mapping in self.mapping.values():
            records.append(SimpleMessage.from_message(mapping.message))
        return records

    # summary: Optional[str] = None
    # @field_validator('mapping')
    # def validate_mapping(cls, value):
    #     for mapping in value.values():
    #         if mapping.message:
    #             validate_content_type(mapping.message.content.content_type, mapping.message.content.model_dump())
    #     return value
