import unittest
import os

from databasetools.adapters.oneNote.oneNote import OneNoteTools

MONGO_URI = os.getenv("MONGO_URI")
TEST_DIR = os.getenv("TEST_DIR")

class TestUpload(unittest.TestCase):
    def setUp(self):
        self.tool = OneNoteTools(MONGO_URI, "test_db", "docBlocks", "rdocBlocks")
        
    def test_upload_dir(self):
        self.tool.upload_dir(TEST_DIR)
        
    def _tearDown(self):
        self.tool.manager.reset_collection()