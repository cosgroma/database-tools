import os
import unittest
from pathlib import Path

from gridfs import GridFS
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from databasetools.controller.mongo_controller import MongoCollectionController
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
        self.manager = DocManager(
            mongo_uri=MONGO_URI, docblock_db_name="TEST_Database", gridFS_db_name="TEST_GridFS", docblock_col_name="TEST_Collection"
        )
        self.manager.reset_collection()
        self.manager.reset_resources()

    def test_init(self):
        assert isinstance(self.manager, DocManager)
        assert self.manager.mongo_uri
        assert self.manager.docblock_db_name
        assert self.manager.gridFS_db_name
        assert self.manager.docblock_col_name

        assert isinstance(self.manager._mongo_client, MongoClient)
        assert isinstance(self.manager._gridFS_db, Database)
        assert isinstance(self.manager._docblock_db, Database)
        assert isinstance(self.manager._gridFS_client, GridFS)
        assert isinstance(self.manager._docblock_col, Collection)
        assert isinstance(self.manager._docblock_col_controller, MongoCollectionController)

        assert self.manager._complete
        assert self.manager._connected

    def test_setters(self):
        man = self.manager
        vital_vars = [man._mongo_uri, man._docblock_db_name, man._gridFS_db_name, man._docblock_col_name]
        connection_vars = [
            man._mongo_client,
            man._gridFS_db,
            man._docblock_db,
            man._gridFS_db,
            man._docblock_col,
            man._docblock_col_controller,
        ]

        for var in vital_vars:
            assert var is not None
        for var in connection_vars:
            assert var is not None

        man.mongo_uri = None
        assert not man._complete
        assert not man._connected

    def test_upload_block(self):
        test_block = DocBlockElement(type=DocBlockElementType.IMAGE)
        return_item = self.manager.upload_block(test_block)
        assert isinstance(return_item, DocBlockElement)

        found_block = self.manager.find_blocks(type=DocBlockElementType.IMAGE.value)
        assert len(found_block) == 1
        assert isinstance(found_block[0], DocBlockElement)

    def tearDown(self):
        # Clear the test database after each test
        self.manager.reset_collection()
        self.manager.reset_resources()
