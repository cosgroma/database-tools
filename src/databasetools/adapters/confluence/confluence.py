import os
import tempfile
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

import mistune
from atlassian.confluence import Confluence
from bson import ObjectId
from mistune.plugins.table import table
from requests_ratelimiter import LimiterSession

from databasetools.adapters.confluence.cf_adapter import image2cf
from databasetools.managers.docs_manager import DocManager
from databasetools.models.docblock import DocBlockElement
from databasetools.models.docblock import DocBlockElementType
from databasetools.utils.docBlock.docBlock_utils import FromDocBlock


class ConfluenceManager:
    def __init__(
        self,
        mongo_uri: str,
        confluence_url: str,
        confluence_space_key: str,
        confluence_username: str,
        confluence_api_token: str,
        mongo_docblock_db_name: str,
        mongo_docblock_collection_name: str,
        mongo_gridFS_db_name: str,
    ):
        self.mongo_man = DocManager(
            mongo_uri=mongo_uri,
            docblock_db_name=mongo_docblock_db_name,
            docblock_col_name=mongo_docblock_collection_name,
            gridFS_db_name=mongo_gridFS_db_name,
        )
        session = LimiterSession(per_second=0.5)
        self.confluence_client = Confluence(
            url=confluence_url, username=confluence_username, password=confluence_api_token, session=session
        )
        self.space_key = confluence_space_key

    def upload_pages(self, page_blocks: Union[List[DocBlockElement], DocBlockElement]):
        if isinstance(page_blocks, DocBlockElement):
            page_blocks = [page_blocks]

        for page_block in page_blocks:
            children_ids = page_block.children
            block_list = self.get_children_block_tree_list(page_block)

            content, required_resources = FromDocBlock.render_docBlock(block_list, children_ids, resource_prefix="RESOURCE")
            conv = mistune.Markdown(renderer=mistune.HTMLRenderer(escape=False), plugins=[table])
            conv.block.list_rules += ["table"]
            html_content = image2cf(conv.parse(content)[0])

            page_name = self.alias_name(page_block.name)
            self.make_confluence_page(
                page_name, html_content, self.get_confluence_page_id("Test Page")
            )  # ---------------------------------------------------------------------------------------------------------------------- REMOVE "Test Page"
            page_id = self.get_confluence_page_id(page_name)
            self.download_and_upload_resource(required_resources, page_id)

    def get_children_block_tree_list(self, block: DocBlockElement) -> List[DocBlockElement]:
        children_ids = block.children
        child_blocks = []
        for id in children_ids:
            child_blocks.extend(self.get_block_tree_list(id))

        return child_blocks

    def get_block_tree_list(self, id: ObjectId) -> List[DocBlockElement]:
        found_blocks = self.mongo_man.find_blocks(id=id)
        if len(found_blocks) != 1:
            raise RuntimeError(f"More than one block found in the database with id: {id}")
        else:
            block_list = [found_blocks[0]]

        for id in block_list[0].children:
            block_list.extend(self.get_block_tree_list(id))

        return block_list

    def download_and_upload_resource(self, resource_names: Union[str, List[str]], page_id: str):
        if isinstance(resource_names, str):
            resource_names = [resource_names]

        temp_dir = Path(tempfile.mkdtemp())

        for name in resource_names:
            name = Path(name)
            filename = name.stem
            ext = name.suffix
            gridout = self.mongo_man.fs_find_file(filename=filename, extension=ext)
            temp_file = temp_dir / name
            with temp_file.open("wb") as f:
                f.write(gridout.read())

        self.add_confluence_attachments(temp_dir, page_id)

        for item in os.listdir(temp_dir):
            (temp_dir / item).unlink()
        temp_dir.rmdir()

    def alias_name(self, title: str):
        numba = 1
        new_title = title
        while self.title_exists(new_title):
            new_title = title + "_" + str(numba)
            numba += 1
        return new_title

    def title_exists(self, title: str):
        result = self.get_confluence_page_id(title)
        return True if result else False

    def get_mongo_page_blocks(self):
        return self.mongo_man.find_blocks(type=DocBlockElementType.PAGE.value)

    def get_confluence_page_id(self, title: str):
        return self.confluence_client.get_page_id(self.space_key, title)

    def make_confluence_page(self, title: str, content: str, parent_id: str):
        return self.confluence_client.create_page(self.space_key, title, content, parent_id)

    def make_confluence_page_directory(self, title: str, parent_id: Optional[str] = None):
        return self.confluence_client.create_page(self.space_key, title, r"{children}", parent_id, representation="wiki")

    def add_confluence_attachments(self, resource_dir: Union[Path, str], page_id: str):
        resource_dir = Path(resource_dir)
        for item in os.listdir(resource_dir):
            item_path = resource_dir / item
            self.confluence_client.attach_file(filename=item_path, page_id=page_id)

    def make_confluence_resource_page(self):
        return self.confluence_client.create_page(self.space_key, "RESOURCES")
