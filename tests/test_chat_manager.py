import os
import unittest
from typing import Any
from typing import Dict
from unittest.mock import patch

import mongomock

from databasetools.managers.chat_manager import ChatManager
from databasetools.models.conversation_model import Author
from databasetools.models.conversation_model import Conversation
from databasetools.models.conversation_model import Mapping
from databasetools.models.conversation_model import Message
from databasetools.models.conversation_model import TextContent

MONGO_URI = os.getenv("MONGO_URI")
print(MONGO_URI)
# Example usage:
# manager = ChatManager(db_uri="mongodb://192.168.50.49:27017", db_name="chatgpt_db_test")
# conversations = manager.load_conversations('path_to_file.json')
# manager.upload_to_mongo(conversations)
# manager.clear_conversation_summaries()
# manager.process_mongo_conversations()


class TestChatManager(unittest.TestCase):
    @patch("pymongo.MongoClient", new=mongomock.MongoClient)
    def setUp(self):
        # Setup a test instance of ChatManager with the mock client
        self.manager = ChatManager(
            db_uri=MONGO_URI,
            db_name="chatgpt_db_test",
        )
        self.test_conversation = Conversation(
            id="conv1",
            conversation_id="conv1",
            conversation_template_id="template1",
            gizmo_id="gizmo1",
            title="Test Conversation",
            default_model_slug="gpt-4",
            create_time=1622559600,
            update_time=1622559600,
            mapping={
                "map1": Mapping(
                    id="map1",
                    parent=None,
                    children=[],
                    message=Message(
                        id="msg1",
                        create_time=1622559600,
                        update_time=1622559600,
                        status="sent",
                        end_turn=False,
                        metadata={},
                        recipient="user",
                        weight=1.0,
                        author=Author(role="user"),
                        content=TextContent(content_type="text", parts=["Hello!"]),
                    ),
                )
            },
            moderation_results=[],
            current_node="node1",
            plugin_ids=[],
            safe_urls=[],
        )

    def test_get_content(self):
        message = self.test_conversation.mapping["map1"].message
        content = self.manager.get_content(message)
        assert content["role"] == "user"
        assert content["content"] == "Hello!"

    def test_upload_to_mongo(self):
        self.manager.upload_to_mongo([self.test_conversation])
        result = self.manager.conversations_collection.find_one({"id": "conv1"})
        assert result
        assert result["id"] == "conv1"
        assert result["title"] == "Test Conversation"

    # def test_process_conversation(self):
    #     processed = self.manager.process_conversation(self.test_conversation)
    #     # self.assertIn("message_set", processed.model_dump())
    #     assert "message_set" in processed.model_dump()
    #     assert len(processed.message_set) == 1
    #     assert processed.message_set[0]["content"] == "Hello!"

    def test_conversation_title(self):
        title = self.test_conversation.title
        assert title == "Test Conversation"

    def test_load_conversations(self):
        conversations = self.manager.load_conversations("tests/test_data/conversations.json")
        assert len(conversations) == 10
        TITLE_LIST = [
            "Comfy UI for diffusion.",
            "Avoid Conversion Char Star",
            "CMake Issue Detection",
            "Python code similarity search",
            "Notion Content Management Tool",
            "Docker Swarm App Deployment",
            "User request, assistant summarize.",
            "Enhance Navigation Accuracy",
            "Python App Discussion",
            "List Implementation Analysis",
        ]
        for i, conv in enumerate(conversations):
            assert conv.title == TITLE_LIST[i]
            print(conv)
            conversation_records: Dict[str, Dict[str, Any]] = {}
            conversation_records[conv.id] = conv.to_records()

        for records in conversation_records.values():
            for message in records:
                assert message.role in ["user", "assistant", "system", "unknown", "tool"]

        assert self.manager.upload_to_mongo(conversations) == 10
        assert self.manager.upload_to_mongo(conversations) == 0
        assert self.manager.upload_to_mongo(conversations, overwrite=True) == 10

    def tearDown(self):
        # Clear the test database after each test
        self.manager.conversations_collection.drop()
