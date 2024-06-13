"""
@brief
@details
@author    Mathew Cosgrove
@date      Friday June 7th 2024
@file      test_conversation_model.py
@copyright (c) 2024 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 06/13/2024 12:44:56
Modified By: Mathew Cosgrove
-----
"""

import json
from pathlib import Path

from databasetools.models.conversation_model import Author
from databasetools.models.conversation_model import Conversation
from databasetools.models.conversation_model import Conversations
from databasetools.models.conversation_model import Mapping
from databasetools.models.conversation_model import Message
from databasetools.models.conversation_model import SimpleMessage
from databasetools.models.conversation_model import TextContent


def test_conversation_model():
    message = Message(
        id="aaa23f00-9117-4700-85fd-e4be81fdf783",
        author=Author(role="user"),
        create_time=1716514617.117903,
        update_time=1716514617.117903,
        end_turn=False,
        status="finished_successfully",
        weight=1.0,
        metadata={
            "request_id": "88898ec28ec62ac1-LAX",
            "timestamp_": "absolute",
        },
        recipient="all",
        content=TextContent(parts=["Hello, World!"]),
    )
    mapping = Mapping(
        id="aaa23f00-9117-4700-85fd-e4be81fdf783",
        parent=None,
        children=None,
        message=message,
    )
    conversation = Conversation(
        id="9bb26374-a22f-4158-923f-5b66f80aa885",
        conversation_id="9bb26374-a22f-4158-923f-5b66f80aa885",
        title="Avoid Conversion Char Star",
        create_time=1716514617.111505,
        update_time=1716514648.140268,
        current_node="e82cb0b0-9f61-41d8-b7ca-32cb887bddb6",
        mapping={"aaa23f00-9117-4700-85fd-e4be81fdf783": mapping},
    )
    print(conversation)
    # print(conversation.to_records())
    # print(conversation.get_messages())
    assert conversation.get_messages()[0].content.parts[0] == "Hello, World!"
    assert conversation.get_messages()[0].author.role == "user"
    assert conversation.get_messages()[0].status == "finished_successfully"
    assert conversation.get_messages()[0].metadata["request_id"] == "88898ec28ec62ac1-LAX"
    assert conversation.get_messages()[0].metadata["timestamp_"] == "absolute"
    assert conversation.get_messages()[0].recipient == "all"


def test_message_model():
    message = Message(
        id="aaa23f00-9117-4700-85fd-e4be81fdf783",
        author=Author(role="user"),
        create_time=1716514617.117903,
        status="finished_successfully",
        weight=1.0,
        metadata={
            "request_id": "88898ec28ec62ac1-LAX",
            "timestamp_": "absolute",
        },
        recipient="all",
        content=TextContent(parts=["Hello, World!"]),
    )
    # print(message)
    assert message.to_simple_message().content == "Hello, World!"


def test_simple_message_model():
    simple_message = SimpleMessage(
        id="aaa23f00-9117-4700-85fd-e4be81fdf783",
        role="user",
        content="Hello, World!",
    )
    print(simple_message)
    message = Message(
        id="aaa23f00-9117-4700-85fd-e4be81fdf783",
        author=Author(role="user"),
        create_time=1716514617.117903,
        status="finished_successfully",
        weight=1.0,
        metadata={
            "request_id": "88898ec28ec62ac1-LAX",
            "timestamp_": "absolute",
        },
        recipient="all",
        content=TextContent(parts=["Hello, World!"]),
    )
    print(SimpleMessage.from_message(message))


SOURCE_EXTENSION_MAP = {
    "python": ".py",
    "javascript": ".js",
    "typescript": ".ts",
    "html": ".html",
    "css": ".css",
    "c": ".c",
    "c++": ".cpp",
    "java": ".java",
    "shell": ".sh",
    "bash": ".sh",
    "powershell": ".ps1",
    "sql": ".sql",
    "yaml": ".yaml",
    "json": ".json",
    "xml": ".xml",
    "markdown": ".md",
    "plaintext": ".txt",
    "text": ".txt",
    "unknown": ".txt",
}


def create_source_file(name, language, content):
    extension = SOURCE_EXTENSION_MAP.get(language, ".txt")
    filename = f"{name}{extension}"
    with Path.open(Path("tests") / "test_data" / filename, "w") as file:
        file.write(content)


def _test_conversations_model_save():
    conversations = Conversations()
    assert conversations
    assert conversations.conversations == []
    conversations.load("tests/test_data/conversations.json")
    title_list = conversations.get_title_list()

    print("\n".join(title_list))
    conversations.save("tests/test_data/conversations_update.json")
    print(f"Average Message Count: {conversations.get_average_message_count()}")
    print(f"Longest Conversation: {conversations.longest_conversation()}")


def _test_conversations_model():
    conversations = Conversations()
    conversations.load("tests/test_data/conversations_long.json")
    print(len(conversations.conversations))
    assert conversations
    print(f"Average Message Count: {conversations.get_average_message_count()}")
    print(f"Longest Conversation: {conversations.longest_conversation()}")
    # title_list = conversations.get_title_list()
    conversation_stats = {}
    for conversation in conversations.conversations:
        conversation_stats[conversation.id] = {"title": conversation.title, "num_messages": len(conversation.get_messages())}

    # save the conversations to a file
    with Path.open("tests/test_data/conversation_stats.json", "w") as file:
        json.dump(conversation_stats, file, indent=4)


# messages = longest_conversation.get_messages()

# for message in messages:
#     source_file = "tests/test_data/python_source.py"

#     # print(message.content.content_type)

#     if message.content.content_type == "text":
#         if md_utils.markdown_has_code_blocks(message.content.text):

#             code_blocks = md_utils.get_code_blocks(message.content.text)
#             for code_block in code_blocks:
#                 print(code_block)
#                 if code_block[1] == "python":
#                     print("Code Appended to File")
#                     with open(source_file, "a") as file:
#                         file.write(code_block[0])
