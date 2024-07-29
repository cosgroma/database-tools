import os
import unittest
from pathlib import Path

from databasetools.managers.docs_manager import DocManager
from databasetools.models.docblock import DocBlockElement
from databasetools.models.docblock import DocBlockElementType

MONGO_URI = os.getenv("MONGO_URI")
TEST_DIR = os.getenv("TEST_DIR")

MONGO_TEST_DB = "test_db"
MONGO_TEST_COLLECTION = "test_collection"

TEST_DIR = Path(TEST_DIR)


class TestDocManager(unittest.TestCase):
    def setUp(self):
        self.manager = DocManager(MONGO_URI)

        self.manager.reset_collections()
        self.manager.reset_grids()

    def test_init(self):
        assert isinstance(self.manager, DocManager)

    def test_upload_block(self):
        test_block = DocBlockElement(type=DocBlockElementType.IMAGE)
        return_item = self.manager.upload_to_col(DocManager.DOC_BLOCKS, test_block)
        assert isinstance(return_item, DocBlockElement)

        found_block = self.manager.find_in_col(collection_name=DocManager.DOC_BLOCKS, type=DocBlockElementType.IMAGE.value)
        assert len(found_block) == 1
        assert isinstance(found_block[0], DocBlockElement)

    def tearDown(self):
        # Clear the test database after each test
        self.manager.reset_collections()
        self.manager.reset_grids()
