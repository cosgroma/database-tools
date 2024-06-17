__version__ = "0.0.0"

# import logging
# import shutil

# import langchain
# import tempfile
# from pprint import pprint
# from dotenv import dotenv_values
from dotenv import load_dotenv

from .adapters.notion import JsonToMdConverter
from .adapters.notion import NotionBlock
from .adapters.notion import NotionClient
from .adapters.notion import NotionDatabase
from .adapters.notion import NotionDownloader
from .adapters.notion import NotionExporter
from .adapters.notion import NotionPage
from .controller.mongo_controller import MongoCollectionController

load_dotenv()  # take environment variables from .env.

# envs = os.environ
# config = dotenv_values(".env")

# # make .dbman directory in home directory
# USER_HOME = os.path.expanduser("~")
# DBMAN_DIR = os.path.join(USER_HOME, ".dbman")
# os.makedirs(DBMAN_DIR, exist_ok=True)

# DIRS_INDEX = {
#     "base": DBMAN_DIR,
#     "dbs": os.path.join(DBMAN_DIR, "dbs"),
#     "kb": os.path.join(DBMAN_DIR, "kb"),
#     "logs": os.path.join(DBMAN_DIR, "logs"),
#     "notebook_exports": os.path.join(DBMAN_DIR, "notebooks"),
#     "notebooks": os.path.join(DBMAN_DIR, "projects"),
#     "projects": os.path.join(DBMAN_DIR, "projects"),
#     "tmp": os.path.join(DBMAN_DIR, "tmp"),
#     "uploads": os.path.join(DBMAN_DIR, "uploads")
# }

# # Make directories in .dbman directory
# for key, value in DIRS_INDEX.items():
#     os.makedirs(value, exist_ok=True)

# NOTEBOOK_EXPORTS = os.path.join(DIRS_INDEX["notebooks"], "md")
# os.makedirs(NOTEBOOK_EXPORTS, exist_ok=True)

# log_verbose = True
# LOG_FORMAT = "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# logging.basicConfig(format=LOG_FORMAT)

# # Log storage path
# LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
# if not os.path.exists(LOG_PATH):
#     os.mkdir(LOG_PATH)

# # Temporary file directory, mainly used for file dialogue
# BASE_TEMP_DIR = os.path.join(tempfile.gettempdir(), "DBMAN")
# try:
#     shutil.rmtree(BASE_TEMP_DIR)
# except Exception:
#     pass
# os.makedirs(BASE_TEMP_DIR, exist_ok=True)

# def make_new_kb_dir(kb_name):
#     kb_dir = os.path.join(DIRS_INDEX["kb"], kb_name)
#     os.makedirs(kb_dir, exist_ok=True)
#     return kb_dir


# def get_kb_file(kb_name, file_name):
#     kb_dir = os.path.join(DIRS_INDEX["kb"], kb_name)
#     return os.path.join(kb_dir, file_name)

# TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "sg_analyst", "templates")

# from jinja2 import Environment, FileSystemLoader
# environment = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

# # get all templates
# # templates = environment.list_templates()

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
