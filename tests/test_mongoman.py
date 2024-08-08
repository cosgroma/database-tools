import os
import traceback
import unittest
from pathlib import Path
from typing import List

from databasetools.managers.mongo_manager import MongoManager
from databasetools.models.docblock import DocBlockElement
from databasetools.models.docblock import PageElement
from databasetools.models.docblock import PageTypes

MONGO_URI = os.getenv("MONGO_URI")
TEST_DIR = os.getenv("TEST_DIR")

MONGO_TEST_DB = "test_db"
MONGO_TEST_COLLECTION = "test_collection"

TEST_DIR = Path(TEST_DIR)

CONFLUENCE_UNAME = os.getenv("CONFLUENCE_UNAME")
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")
CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_API_KEY")


class TestMongMan(unittest.TestCase):
    def test_init(self):
        new_grid_name = "snook"
        newer_grid_name = "spoop"
        new_col_name = "snek"
        new_col = (new_col_name, DocBlockElement)
        newer_col_name = "snerk"
        newer_col = (newer_col_name, PageElement)
        new_db_db_name = "dbdbdbdbdb_WOOOOO"

        mongo_man = MongoManager(MONGO_URI, CONFLUENCE_URL, CONFLUENCE_SPACE_KEY, CONFLUENCE_UNAME, CONFLUENCE_TOKEN)
        assert mongo_man
        assert mongo_man.active_grid == MongoManager.RESOURCES
        assert mongo_man.active_db_col == MongoManager.DOC_BLOCKS
        assert mongo_man.active_page_col == MongoManager.PAGE_DATA

        mongo_man.active_grid = new_grid_name
        assert mongo_man.active_grid == new_grid_name

        mongo_man.active_db_col = new_col
        assert mongo_man.active_db_col == new_col_name

        mongo_man.active_page_col = newer_col
        assert mongo_man.active_page_col == newer_col_name

        assert len(mongo_man._grids) == 2
        grid_names = [MongoManager.RESOURCES, new_grid_name]
        for name in grid_names:
            assert name in mongo_man._grids

        assert len(mongo_man._collections) == 4
        collection_names = [MongoManager.DOC_BLOCKS, MongoManager.PAGE_DATA, new_col_name, newer_col_name]
        for name in collection_names:
            assert name in mongo_man._collections

        mongo_man = MongoManager(MONGO_URI, new_db_db_name, new_grid_name, new_col)
        assert mongo_man.active_grid == MongoManager.RESOURCES
        assert mongo_man.active_db_col == MongoManager.DOC_BLOCKS
        assert mongo_man.active_page_col == MongoManager.PAGE_DATA
        assert len(mongo_man._grids) == 2
        assert len(mongo_man._collections) == 3

        mongo_man.active_grid = new_grid_name
        mongo_man.active_db_col = new_col
        mongo_man.active_page_col = new_col
        assert mongo_man.active_grid == new_grid_name
        assert mongo_man.active_db_col == new_col_name
        assert mongo_man.active_page_col == new_col_name
        assert len(mongo_man._grids) == 2
        assert len(mongo_man._collections) == 3

        mongo_man = MongoManager(MONGO_URI, new_db_db_name, [new_grid_name, newer_grid_name], [new_col, newer_col])
        assert mongo_man.active_grid == MongoManager.RESOURCES
        assert mongo_man.active_db_col == MongoManager.DOC_BLOCKS
        assert mongo_man.active_page_col == MongoManager.PAGE_DATA
        assert len(mongo_man._grids) == 3
        assert len(mongo_man._collections) == 4

        mongo_man.active_grid = new_grid_name
        mongo_man.active_db_col = new_col
        mongo_man.active_page_col = newer_col
        assert mongo_man.active_grid == new_grid_name
        assert mongo_man.active_db_col == new_col_name
        assert mongo_man.active_page_col == newer_col_name
        assert len(mongo_man._grids) == 3
        assert len(mongo_man._collections) == 4

    def test_full_upload(self):
        mm = MongoManager(MONGO_URI, CONFLUENCE_URL, CONFLUENCE_SPACE_KEY, CONFLUENCE_UNAME, CONFLUENCE_TOKEN, "TEST_2", "TEST_2_Grid")
        export_element: List[PageElement] = mm.find_in_col(mm.active_page_col, type=PageTypes.EXPORT)
        if export_element:
            export_id = export_element[0].id
        else:
            export_id = mm.upload_one_note(TEST_DIR)
        try:
            mm.upload_confluence(export_id, parent_title="Test Page")
        except BaseException as e:
            tempfile = Path("./log.temp")
            with tempfile.open("w") as f:
                traceback.print_exc(file=f)
            raise e
