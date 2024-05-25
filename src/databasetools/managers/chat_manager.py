import json
from pathlib import Path
from typing import List

from pymongo import MongoClient

from ..models.conversation_model import Conversation


class ChatManager:
    """A class to manage chat conversations and upload them to a MongoDB database.

    Attributes:
        client (MongoClient): The MongoDB client.
        db (Database): The MongoDB database.
        conversations_collection (Collection): The MongoDB collection to store conversations.

    Methods:
        get_content(message: Message) -> Dict[str, Any]:
            Extracts the role and content from a message.
        upload_to_mongo(conversations: List[Conversation]):
            Uploads a list of conversations to the MongoDB collection.
        load_conversations(file_path: str) -> List[Conversation]:
            Loads conversations from a JSON file.
    """

    def __init__(self, db_uri: str, db_name: str, conversation_collection_name: str = "conversations"):
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.conversations_collection = self.db[conversation_collection_name]
        self.logs = self.db["chat_manager_logs"]

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
        self.logs.insert_one({"action": "load_conversations", "file_path": file_path, "num_conversations": len(conversations)})
        return conversations

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

    def find_all_zips(self, dir_path: str):
        zip_files = []
        # CHATGPT_USER_ID = os.environ.get("CHATGPT_USER_ID")
        for file in Path(dir_path).iterdir():
            if file.suffix == ".zip":
                zip_files.append(file)
        return zip_files

    def extract_all_zips(self, zip_files: List[str], output_dir: str):
        for zip_file in zip_files:
            print(f"Extracting {zip_file} to {output_dir}")
            # extract zip file to output_dir
