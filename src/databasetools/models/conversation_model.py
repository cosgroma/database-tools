from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import field_validator

# "content_type": "code",


class MessageContent(BaseModel):
    content_type: str
    parts: Optional[List[str] | List[Dict[str, Any]]] = None
    language: Optional[str] = None
    response_format_name: Optional[str] = None
    text: Optional[str] = None


# {
#     "content_type": "text",
#     "parts": [
#         "example text"
#     ]
# },
class TextContent(BaseModel):
    content_type: str = "text"
    parts: List[str]


# {
#     "content_type": "code",
#     "language": "unknown",
#     "response_format_name": null,
#     "text": "import markdown\n\ncontent = \"\"\"\n# App Design Summary\n\n## Key Concepts and Objectives\n\nThe app is designed to support flow-based programming and system modeling, leveraging the four pillars of SysML (Requirements, Behavior, Structure, and Parametrics) and the Unified Architecture Framework (UAF). Additionally, it integrates the OODA (Observe, Orient, Decide, Act) loop for structured decision-making processes.\n\n## Primary Swim Lanes\n\n1. **Requirements**: Capture and organize system requirements.\n2. **Behavior**: Model the dynamic behavior of the system.\n3. **Structure**: Define the static structure of the system.\n4. **Parametrics**: Model performance constraints and quantitative relationships.\n\n## Key Features\n\n1. **Viewpoint Configuration**: Allow users to define and configure viewpoints dynamically.\n2. **Flexible Swim Lanes**: Enable the app to adapt to different swim lane structures based on the chosen viewpoint.\n3. **Node Abstraction**: Design nodes to be flexible and reusable across different viewpoints.\n\n## Node Types\n\n### Requirements Swim Lane\n- **Requirement Node**: Captures a specific requirement.\n- **Requirement Aggregation Node**: Aggregates multiple requirements.\n- **LLM Interaction Node**: Refines and generates requirements using an LLM.\n- **Traceability Node**: Links requirements to subsequent models for traceability.\n\n### Behavior Swim Lane\n- **Activity Node**: Represents actions or processes.\n- **State Machine Node**: Models state transitions.\n- **Use Case Node**: Defines scenarios and interactions.\n- **Sequence Diagram Node**: Captures the order of interactions.\n- **LLM Interaction Node**: Generates behavior models from requirements.\n- **Validation Node**: Ensures behaviors meet requirements.\n\n### Structure Swim Lane\n- **Component Node**: Represents system components.\n- **Connection Node**: Defines relationships between components.\n- **Subsystem Node**: Groups related components.\n- **Interface Node**: Details how components interact.\n- **LLM Interaction Node**: Assists in generating structural models.\n- **Configuration Node**: Manages component configurations.\n\n### Parametrics Swim Lane\n- **Parameter Node**: Defines key parameters and constraints.\n- **Relationship Node**: Models quantitative relationships between parameters.\n- **Optimization Node**: Assists in optimizing parameters to meet constraints.\n- **Simulation Node**: Runs simulations to test parametric models.\n- **LLM Interaction Node**: Helps define and refine parametric models.\n- **Metrics Node**: Tracks performance metrics and criteria.\n\n## OODA Loop Integration\n\n### Observe Phase\n- **Data Fetching Nodes**: Retrieve data from databases, APIs, or other sources.\n- **Contextual Information Nodes**: Gather additional context or environmental information.\n\n### Orient Phase\n- **Data Processing Nodes**: Process, clean, and transform raw data.\n- **Correlation Nodes**: Find relationships and patterns within the data.\n- **Visualization Nodes**: Create visual representations of data for better understanding.\n\n### Decide Phase\n- **Decision Support Nodes**: Evaluate options based on criteria and constraints.\n- **Optimization Nodes**: Optimize potential actions based on performance metrics.\n\n### Act Phase\n- **Action Nodes**: Execute specific actions or commands.\n- **Execution Monitoring Nodes**: Monitor the execution of actions and report outcomes.\n\n## Additional Flow Graphs\n\n### Sprint Planning Flow\n1. **Fetch Issues**\n2. **Prioritize Issues**\n3. **Define Sprint Goals**\n4. **Assign Tasks**\n5. **Create Sprint in JIRA**\n\n### Story Generation Flow\n1. **Gather Requirements**\n2. **Generate User Stories**\n3. **Review and Refine Stories**\n4. **Create Stories in JIRA**\n\n### Program Increment Planning Flow\n1. **Fetch Epics**\n2. **Define Increment Goals**\n3. **Align Teams**\n4. **Create Increment in JIRA**\n\n### Task Assignment and Tracking Flow\n1. **Fetch Backlog**\n2. **Assign Tasks**\n3. **Track Progress**\n4. **Update Task Status in JIRA**\n\n### Progress Monitoring and Reporting Flow\n1. **Fetch Sprint Data**\n2. **Analyze Progress**\n3. **Generate Reports**\n4. **Distribute Reports**\n\n## Key Design Decisions\n\n1. **Viewpoint Flexibility**: The app is designed to accept different viewpoint specifications, allowing for flexible swim lane construction.\n2. **Integration with JIRA**: Supports sprint planning, story generation, and program increment planning through seamless integration with JIRA.\n3. **OODA Loop Integration**: Incorporates the OODA loop to guide states and interactions within the system.\n4. **Node Flexibility and Reusability**: Nodes are designed to be flexible and reusable across different viewpoints and swim lanes.\n5. **Real-time Collaboration and Version Control**: Supports real-time collaboration and version control to enhance productivity and team collaboration.\n\nBy implementing these features, the app aims to provide a comprehensive and adaptable environment for system modeling and flow-based programming, supporting various methodologies like SysML and UAF.\n\n\"\"\"\n\nwith open(\"/mnt/data/App_Design_Summary.md\", \"w\") as file:\n    file.write(content)\n\n\"/mnt/data/App_Design_Summary.md\""
# },
class CodeContent(BaseModel):
    content_type: str = "code"
    language: Optional[str] = "unknown"
    response_format_name: Optional[str] = None
    text: Optional[str] = None


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
# "parts": [
# ]
class MultimodalTextContent(BaseModel):
    content_type: str = "multimodal_text"
    parts: Optional[List[Dict[str, Any]]]


# {
#     "content_type": "execution_output",
#     "text": "'/mnt/data/App_Design_Summary.md'"
# },


class ExecutionOutputContent(BaseModel):
    content_type: str = "execution_output"
    text: Optional[str]


# {
#     "role": "user",
#     "name": null,
#     "metadata": {}
# },
class Author(BaseModel):
    role: str
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


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


# "content_type": "multimodal_text",
# "content_type": "text",
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
# }
class Mapping(BaseModel):
    id: str
    parent: Optional[str]
    children: Optional[List[str]]
    message: Optional[Message]


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
    title: str
    default_model_slug: str
    conversation_id: str
    conversation_template_id: Optional[str]
    gizmo_id: Optional[str]
    create_time: float
    update_time: float
    current_node: Optional[str]
    moderation_results: Optional[List[Any]]
    plugin_ids: Optional[List[str]]
    safe_urls: Optional[List[str]]
    mapping: Dict[str, Mapping]
    # message_set: Optional[List[Dict[str, Any]]] = None
    # summary: Optional[str] = None
    # @field_validator('mapping')
    # def validate_mapping(cls, value):
    #     for mapping in value.values():
    #         if mapping.message:
    #             validate_content_type(mapping.message.content.content_type, mapping.message.content.model_dump())
    #     return value
