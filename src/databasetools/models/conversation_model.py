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
from pydantic import computed_field
from pydantic import field_validator

import json
from pathlib import Path
        

class TextContent(BaseModel):
    content_type: str = "text"
    parts: List[str]

    @computed_field(return_type=str)
    @property
    def text(self):
        return " ".join(self.parts)
    
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
    
    def append_code_to_file(self, file_path: str):
        with open(file_path, "a") as file:
            file.write(f"{self.text}")
            file.write("\n")
        
        


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

import uuid

def generate_uuid():
    return str(uuid.uuid4())

class SimpleMessage(BaseModel):
    id: str
    role: str
    content: str = ""
    tags: Optional[List[str]] = None

    @computed_field(return_type=str)
    @property
    def summary(self):
        return self.content[:20]
    
    @field_validator("id", mode="before")
    def validate_id(cls, value):
        if value is None:
            return generate_uuid()
        return value
    
    @field_validator("tags")
    def validate_tags(cls, value):
        if value is None:
            return []
        return value
    
    @field_validator("role")
    def validate_role(cls, value):
        if value is None:
            return "unknown"
        return value
    
    def __str__(self):
        return f"{self.role}: {self.content:20}..."

    @classmethod
    def from_message(cls, message: "Message") -> "SimpleMessage":
        if message is None:
            return cls(role="unknown", content="")
        content = str(message.content) if message.content is not None else ""
        role = message.author.role if message.author is not None else "unknown"
        return cls(id=message.id, role=role, content=content)
    
class Message(BaseModel):
    id: str
    author: Author
    create_time: Optional[float]
    update_time: Optional[float] = None
    status: str
    end_turn: Optional[bool] = False
    recipient: str
    weight: float
    metadata: Dict[str, Any]
    conversation_id: Optional[str] = None
    parent_message_id: Optional[str] = None

    content: Union[TextContent, CodeContent, MultimodalTextContent]

    @field_validator("content")
    def validate_content(cls, value):
        validate_content_type(value.content_type, value.model_dump())
        return value

    def to_simple_message(self) -> SimpleMessage:
        content = str(self.content) if self.content is not None else ""
        role = self.author.role if self.author is not None else "unknown"
        return SimpleMessage(id=self.id, role=role, content=content)
    
    def __str__(self):
        content = str(self.content) if self.content is not None else ""
        
        return f"[{self.author.role}, {self.weight}]: {content:20}..."
    
    def content_is_code(self):
        return self.content.content_type == "code"



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
    parent: Optional[str] = ""
    children: Optional[List[str]] = []
    message: Optional[Message]

    def __str__(self):
        message = "" if self.message is None else self.message
        parent = "" if self.parent is None else self.parent
        return f"[{parent:5}]{self.id:5} -> {message:20}..."


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
    moderation_results: Optional[List[Any]] = []
    plugin_ids: Optional[List[str]] = None
    safe_urls: Optional[List[str]] = None
    mapping: Dict[str, Mapping]
    tags: Optional[List[str]] = None
    
    @computed_field(return_type=int)
    @property
    def num_messages(self):
        return len(self.mapping)

    def __str__(self):
        return f"[{self.default_model_slug}]:({self.title},{self.num_messages})"

    def to_records(self) -> List[SimpleMessage]:
        records = []
        for mapping in self.mapping.values():
            records.append(SimpleMessage.from_message(mapping.message))
        return records
    
    def get_messages(self) -> List[Message]:
        messages = []
        for mapping in self.mapping.values():
            message = mapping.message
            if message is None:
                print(f"Message is None: {mapping}")
                continue
            message.conversation_id = self.id
            mapping_parent = self.mapping[mapping.parent] if mapping.parent else None
            if mapping_parent is None:
                message.parent_message_id = None
            else:
                if mapping_parent.message is None:
                    print(f"Parent message is None: {mapping_parent}")
                    continue
                message.parent_message_id = mapping_parent.message.id
            messages.append(mapping.message)
        return messages
    
    def add_mapping(self, mapping: Mapping):
        self.mapping[mapping.id] = mapping
    
    def remove_mapping(self, mapping_id: str) -> Optional[Mapping]:
        return self.mapping.pop(mapping_id, None)
    
    def get_mapping(self, mapping_id: str) -> Optional[Mapping]:
        return self.mapping.get(mapping_id, None)
    
    def get_parent_mapping(self, mapping_id: str) -> Optional[Mapping]:
        mapping = self.get_mapping(mapping_id)
        if mapping is None:
            return None
        return self.get_mapping(mapping.parent)
    
        
class Conversations(BaseModel):
    conversations: Optional[List[Conversation]] = []
    
    def rm(self, conversation_id: str) -> Optional[Conversation]:
        for i, conversation in enumerate(self.conversations):
            if conversation.id == conversation_id:
                return self.conversations.pop(i)
        return None
    
    def add(self, conversation: Conversation):
        self.conversations.append(conversation)
    
    def load(self, file_path: str) -> List[Conversation]:
        if not Path.is_file(Path(file_path)):
            print(f"File {file_path} does not exist")
            return []
        with Path.open(file_path) as file:
            data = json.load(file)
            for conv in data:
                try:
                    self.conversations.append(Conversation(**conv))
                except Exception as e:
                    print(f"Error loading conversation: {e}")
            return self.conversations
    
    def save(self, file_path: str):
        with Path.open(file_path, "w") as file:
            json.dump([conv.model_dump() for conv in self.conversations], file)
            
    def __str__(self):
        return f"Conversations({len(self.conversations)})"
    
    def get_title_list(self) -> List[str]:
        return [conv.title for conv in self.conversations if conv.title is not None]
    
    def get_average_message_count(self) -> float:
        return sum([conv.num_messages for conv in self.conversations]) / len(self.conversations)
    
    def longest_conversation(self) -> Conversation:
        return max(self.conversations, key=lambda conv: conv.num_messages)

    # summary: Optional[str] = None
    # @field_validator('mapping')
    # def validate_mapping(cls, value):
    #     for mapping in value.values():
    #         if mapping.message:
    #             validate_content_type(mapping.message.content.content_type, mapping.message.content.model_dump())
    #     return value



    
    