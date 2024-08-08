import logging
import os
import unittest
from pathlib import Path

from atlassian import Confluence
from requests import Session
from requests_ratelimiter import HTTPAdapter
from urllib3.util import Retry

import databasetools.adapters.confluence.cf_adapter as cf
from databasetools.managers.mongo_manager import MongoManager

MONGO_URI = os.getenv("MONGO_URI")
TEST_DIR = os.getenv("TEST_DIR")

MONGO_TEST_DB = "test_db"
MONGO_TEST_COLLECTION = "test_collection"

TEST_DIR = Path(TEST_DIR)

CONFLUENCE_UNAME = os.getenv("CONFLUENCE_UNAME")
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")
CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_API_KEY")

logger = logging.getLogger("MongoMan Logger")


class TestCFAdapter(unittest.TestCase):
    def _test_html_pptx_link_2_cf_pptx(self):
        test_str = (
            """<p><a href="https://confluence.northgrum.com/cac37417528a4512b83e7360eed7e93e.pptx">FTUAS Agenda 20220331.pptx</a></p>"""
        )

        assert cf.html_pptx_link_2_cf_pptx(test_str)

    def _test_debug_tree(self):
        id = "906360785"
        mm = MongoManager(MONGO_URI, CONFLUENCE_URL, CONFLUENCE_SPACE_KEY, CONFLUENCE_UNAME, CONFLUENCE_TOKEN, "TEST_2", "TEST_2_Grid")
        mm.del_in_grid(mm.active_grid, confluence_id=id)

    def test_dumb_thing(self):
        session = Session()
        retries = Retry(total=1000, backoff_factor=0.1, status_forcelist=[502, 503, 504], allowed_methods=False)
        session.mount("https://", HTTPAdapter(max_retries=retries))
        self.confluence_client = Confluence(
            url=CONFLUENCE_URL, username=CONFLUENCE_UNAME, password=CONFLUENCE_TOKEN, timeout=600, session=session
        )
        result = self.confluence_client.get_page_by_title(CONFLUENCE_SPACE_KEY, "2020 Holiday Schedule FAQs ")
        print(result)
