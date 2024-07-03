import os
import unittest
import mongomock
import json
from unittest.mock import patch
from pathlib import Path
from databasetools.managers.docs_manager import DocManager
from databasetools.models.mof_model import Relation, Element, ElementType
from databasetools.adapters.oneNote.oneNote import OneNoteMd2Json 

MONGO_URI = os.getenv("MONGO_URI")
TEST_DIR = os.getenv("TEST_DIR")

MONGO_TEST_DB = "test_db"
MONGO_TEST_COLLECTION = "test_collection"

TEST_DIR = Path(TEST_DIR)

class TestDocManager(unittest.TestCase):
    @patch("pymongo.MongoClient", new=mongomock.MongoClient)
    def setUp(self):
        self.manager = DocManager(
            db_uri=MONGO_URI,
            db_name="docs_test_db"
        )
        self.oneNote = OneNoteMd2Json()
        self.test_relation = Relation(
            source_id="1111",
            destination_id="2222",
            relation_type="one_to_many"
        )
        self.test_block1 = Element(
            element_id="0000",
            name="Element 1",
            element_type=ElementType.GENERIC,
            labels=["Element 1 Label 1", "Element 1 Label 2"]
        )
        self.test_block2 = Element(
            element_id="0001",
            name="Element 2",
            element_type=ElementType.USER,
            labels=["Element 2 Label 1", "Element 2 Label 2"]
        )
    
    def test_init(self):
        self.assertIsNotNone(self.manager)

    def test_parse_oneNote_export(self):
        content = self.oneNote.parse_oneNote_export2(TEST_DIR / "source" / "Platform Library.md")
        jstring = json.dumps(content, default=str)
        di = json.dumps(content["content"], default=str)
        with open(Path(TEST_DIR / "dump" / "dump.json"), "w") as f:
            f.write(jstring)

    def test_upload_relation(self):
        self.assertTrue(self.manager.upload_relation(self.test_relation))
        result = self.manager.relations_collection.find_one({"source_id": "1111"})
        assert result
        self.assertEqual(result["source_id"], "1111")
        self.assertEqual(result["destination_id"], "2222")
        self.assertEqual(result["relation_type"], "one_to_many")

    def test_upload_block(self):
        self.assertTrue(self.manager.upload_block(self.test_block1))
        result = self.manager.blocks_collection.find_one({"element_id": "0000"})
        assert result 
        self.assertEqual(result["name"], "Element 1")
        self.assertEqual(result["element_type"], ElementType.GENERIC)
        self.assertTrue(self.manager.upload_block(self.test_block2))
        doc_count = self.manager.blocks_collection.count_documents({})
        self.assertEqual(doc_count, 2)
   
    def tearDown(self):
        # Clear the test database after each test
        self.manager.relations_collection.drop()
        self.manager.blocks_collection.drop()

    
