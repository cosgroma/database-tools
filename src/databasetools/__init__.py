__version__ = "0.0.0"

from dotenv import load_dotenv

from .adapters.notion import JsonToMdConverter
from .adapters.notion import NotionBlock
from .adapters.notion import NotionClient
from .adapters.notion import NotionDatabase
from .adapters.notion import NotionDownloader
from .adapters.notion import NotionExporter
from .adapters.notion import NotionPage
from .controller.mongo_controller import MongoCollectionController

load_dotenv()  # take environment variables


# MONGO_DB = os.getenv("MONGO_DB")


__all__ = [
    "JsonToMdConverter",
    "NotionClient",
    "NotionDatabase",
    "NotionPage",
    "NotionDownloader",
    "NotionExporter",
    "NotionBlock",
    "MongoCollectionController",
]
