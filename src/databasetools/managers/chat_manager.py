import json
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from pymongo import MongoClient

from ..models.conversation_model import Conversation
from ..models.conversation_model import Message


class ChatManager:
    """A class to manage chat conversations and upload them to a MongoDB database.

    Attributes:
        client (MongoClient): The MongoDB client.
        db (Database): The MongoDB database.
        conversations_collection (Collection): The MongoDB collection to store conversations.

    Methods:
        get_content(message: Message) -> Dict[str, Any]:
            Extracts the role and content from a message.
        process_conversation(conversation: Conversation) -> Conversation:
            Processes a conversation by generating the message set, summary, and tags.
        upload_to_mongo(conversations: List[Conversation]):
            Uploads a list of conversations to the MongoDB collection.
        process_mongo_conversations():
            Processes all conversations in the MongoDB collection.
        clear_conversation_summaries():
            Clears the summaries of all conversations in the MongoDB collection.
        get_summary_and_tags(conversation: Conversation) -> (str, List[str]):
            Generates a summary and tags for a conversation.
        load_conversations(file_path: str) -> List[Conversation]:
            Loads conversations from a JSON file.
    """

    def __init__(self, db_uri: str, db_name: str, conversation_collection_name: str = "conversations"):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.conversations_collection = self.db[conversation_collection_name]

    def get_content(self, message: Message) -> Dict[str, Any]:
        try:
            role = message.author.role
            content = message.content
            content_str = "".join(content.parts)
            return {"role": role, "content": content_str}
        except Exception as e:
            print(f"Error getting content: {e} {message}")
            return {"role": "", "content": ""}

    def process_conversation(self, conversation: Conversation) -> Conversation:
        if not conversation.message_set:
            print(f"{conversation.title}:: Getting Message Set")
            processed_mapping = []
            for mapping in conversation.mapping.values():
                processed_mapping.append(self.get_content(mapping.message))
            conversation.message_set = processed_mapping

        if not conversation.summary:
            print(f"{conversation.title}:: Generating Summary and Tags")
            summary, tags = self.get_summary_and_tags(conversation)
            conversation.summary = summary
            for i, message in enumerate(conversation.message_set):
                if i < len(tags):
                    message["tags"] = tags[i]

        return conversation

    def upload_to_mongo(self, conversations: List[Conversation], overwrite: bool = False) -> int:
        uploaded = 0
        # check that the conversation doesn't already exist in the collection
        for conversation in conversations:
            if len(list(self.conversations_collection.find({"id": conversation.id}))) > 0:
                if not overwrite:
                    print(f"Conversation {conversation.id} already exists in the collection, skipping, add overwrite=True to overwrite")
                    continue
                else:
                    print(f"Overwriting conversation {conversation.id}")
            self.conversations_collection.update_one({"id": conversation.id}, {"$set": conversation.model_dump()}, upsert=True)
            uploaded += 1
        return uploaded

    # def process_mongo_conversations(self):
    #     conversations = list(self.conversations_collection.find())
    #     for conv_dict in conversations:
    #         try:
    #             conversation = Conversation(**conv_dict)
    #             conversation_update = self.process_conversation(conversation)
    #             self.conversations_collection.update_one({"id": conversation.id}, {"$set": conversation_update.model_dump()}, upsert=True)
    #         except ValidationError as e:
    #             print(f"Validation error: {e}")

    def load_conversations(self, file_path: str) -> List[Conversation]:
        with Path.open(file_path) as file:
            data = json.load(file)
            conversations = []
            for conv in data:
                try:
                    conversation = Conversation(**conv)
                    conversations.append(conversation)
                except Exception as e:
                    print(f"Error: {e} for conversation: {conv['title']}")
        return conversations


# Example usage:
# manager = ChatManager(db_uri="mongodb://192.168.50.49:27017", db_name="chatgpt_db_test", username="root", password="example")
# conversations = manager.load_conversations('path_to_file.json')
# manager.upload_to_mongo(conversations)
# manager.clear_conversation_summaries()
# manager.process_mongo_conversations()
