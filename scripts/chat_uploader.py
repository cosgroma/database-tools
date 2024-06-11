# The project idea involves extracting user role messages from a MongoDB collection:
# analyzing them for similarities, creating conversation threads in a Notion database, and refining the threads into templates.
#
# The implementation will involve steps such as:
#
# * extracting messages from MongoDB
# * storing data in Notion
# * finding similarities among messages using NLP techniques
# * creating conversation threads in Notion programmatically
# * refining threads into templates
#
# Challenges include NLP and clustering, Notion API integration, data preprocessing, and scalability.

"""Usage: chat_manager.py [-vqh] upload [FILE] [-n] ...
          chat_manager.py [-vqh] stats
          chat_manager.py [-vqh] (-i | --interactive)
          chat_manager.py [-vqh] --version

The most commonly used chat_manager.py commands are:
    upload      Upload conversations to MongoDB.
    stats       Show statistics about the conversations.
    interactive Run the chat manager in interactive mode.
    version     Show the version of the chat manager.

Commands:
    upload  Upload conversations to MongoDB.
    stats   Show statistics about the conversations.

Arguments:
    FILE  The JSON file containing the conversations.

Options:
    -h --help     Show this screen.
    -v --verbose  Show extra information.
    -q --quiet    Hide output.
    -n --dry-run  Perform a dry run.
    -i --interactive  Run the chat manager in interactive mode.
    --version     Show version.

Examples:
    chat_manager.py upload conversations.json -n
    chat_manager.py stats
    chat_manager.py -i
    chat_manager.py --version
"""
import os
import sys

import dotenv
from docopt import docopt

from databasetools.managers.chat_manager import ChatManagerv0 as ChatManager

dotenv.load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
manager = ChatManager(db_uri=MONGO_URI, db_name="chatgpt_db")


# class Recording(Page):
#     ref = TitleText("Ref")
#     file_path = Text("File Path")
#     size_bytes = Number("Size Bytes")
#     length_seconds = Number("Length Seconds")
#     upload_date = Date("Upload Date")
#     processed = Checkbox("Processed")

#     def __str__(self):
#         return f"Recording({self.ref}, {self.file_path}, {self.size_bytes})"


# def test_notion_database_class():
#     assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
#     assert TEST_PLANNING_PAGE_URL, "TEST_PLANNING_PAGE_URL not set, set it in .env file"
#     DB_URL = "https://www.notion.so/cosgroma/62c81d1feaaf485288b4758ec7516b89?v=380a231034534e04b678fd0c80d4ccf9&pvs=4"
#     # DB_ID = "62c81d1feaaf485288b4758ec7516b89"
#     DB_ID = utils.extract_id_from_notion_url(DB_URL)
#     # test_db = NotionDatabase(token=NOTION_API_KEY, database_id=DB_ID, DataClass=Task)

#     test_db = NotionDatabase(token=NOTION_API_KEY, database_id=DB_ID, DataClass=Recording)


def main():

    args = docopt(__doc__, version="Chat Uploader 1.0")
    print(args)

    if args["upload"]:
        if args["FILE"]:
            conversations = manager.load_conversations(args["FILE"])
            print(f"Loaded {len(conversations)} conversations.")
            upload_count = 0
            if not args["--dry-run"]:
                upload_count = manager.upload_to_mongo(conversations)
            print(f"Uploaded {upload_count} conversations.")
        else:
            print("No file provided.")

    elif args["stats"]:
        print("Showing conversation statistics...")
        # manager.process_mongo_conversations()

    elif args["interactive"]:
        print("Running chat manager in interactive mode...")

    else:
        print("Invalid command.")
        sys.exit(1)


if __name__ == "__main__":
    main()
