import unittest
import os

from databasetools.adapters.oneNote.oneNote import OneNoteTools
from databasetools.managers.docs_manager import DocManager

DB_NAME = "test_oneNote_upload"
MONGO_URI = os.getenv("MONGO_URI")
TEST_DIR = os.getenv("TEST_DIR")
RESOURCES = os.getenv("RESOURCES")

class TestUpload(unittest.TestCase):
    def setUp(self):
        self.tool = OneNoteTools(MONGO_URI, "test_db", "docBlocks", "rdocBlocks")
    
    def _test_reset_resources(self):
        self.tool.manager.reset_resources()
        
    def test_upload_oneNote_export(self):
        self.tool.manager.reset_resources()
        self.tool.manager.reset_collection()
        missed = self.tool.upload_oneNote_export(TEST_DIR)
        assert not missed
        missing_resource = self.tool.verify_references()
        assert not missing_resource
        
    def _test_get_resource(self):
        data = self.tool.get_resource("003635cb420941afacda1cf27caa921c", ".jpg")
        assert data
        assert isinstance(data, bytes)
    
    def _test_upload_dir(self):
        self.tool.upload_dir(TEST_DIR)
        
    def _test_upload_resources(self):
        self.tool.store_resources(RESOURCES)
        
    def _tearDown(self):
        self.tool.manager.reset_collection()