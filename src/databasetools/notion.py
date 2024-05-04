import json
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from notion_client import Client
from notion_client.helpers import iterate_paginated_api as paginate
from notion_objects import Database
from notion_objects import Page

from .utils import logger
from .utils import normalize_id


class NotionDownloader:
    def __init__(self, token: str, filter: Optional[str] = None):
        self.transformer = LastEditedToDateTime()
        self.notion = NotionClient(token=token, transformer=self.transformer, filter=filter)
        self.io = NotionIO(self.transformer)

    def download_url(self, url: str, out_dir: Union[str, Path] = "./json"):
        """Download the notion page or database."""
        out_dir = Path(out_dir)
        slug = url.split("/")[-1].split("?")[0]
        if "-" in slug:
            page_id = slug.split("-")[-1]
            self.download_page(page_id, out_dir / f"{page_id}.json")
        else:
            self.download_database(slug, out_dir)

    def download_page(self, page_id: str, out_path: Union[str, Path] = "./json", fetch_metadata: bool = True):
        """Download the notion page."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        blocks = self.notion.get_blocks(page_id)
        self.io.save(blocks, out_path)

        if fetch_metadata:
            metadata = self.notion.get_metadata(page_id)
            self.io.save([metadata], out_path.parent / "database.json")

    def download_database(self, database_id: str, out_dir: Union[str, Path] = "./json"):
        """Download the notion database and associated pages."""
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "database.json"
        prev = {pg["id"]: pg["last_edited_time"] for pg in self.io.load(path)}
        pages = self.notion.get_database(database_id)  # download database
        self.io.save(pages, path)

        for cur in pages:  # download individual pages in database IF updated
            if prev.get(cur["id"], datetime(1, 1, 1, tzinfo=cur["last_edited_time"].tzinfo)) < cur["last_edited_time"]:
                self.download_page(cur["id"], out_dir / f"{cur['id']}.json", False)
                logger.info(f"Downloaded {cur['url']}")


class LastEditedToDateTime:
    def forward(self, blocks, key: str = "last_edited_time") -> List:
        return [
            {
                **block,
                "last_edited_time": datetime.fromisoformat(block["last_edited_time"][:-1]),
                "id": normalize_id(block["id"]),
            }
            for block in blocks
        ]

    def reverse(self, o) -> Union[None, str]:
        if isinstance(o, datetime):
            return o.isoformat() + "Z"


class NotionIO:
    def __init__(self, transformer):
        self.transformer = transformer

    def load(self, path: Union[str, Path]) -> List[dict]:
        """Load blocks from json file."""
        if Path(path).exists():
            with Path.open(path) as f:
                return self.transformer.forward(json.load(f))
        return []

    def save(self, blocks: List[dict], path: str):
        """Dump blocks to json file."""
        with Path.open(path, "w") as f:
            json.dump(blocks, f, default=self.transformer.reverse, indent=4)


class NotionClient:
    def __init__(self, token: str, transformer: LastEditedToDateTime = None, filter: Optional[dict] = None):
        self.client = Client(auth=token)
        if transformer is None:
            transformer = LastEditedToDateTime()
        self.transformer = transformer
        self.filter = filter
        self.database_records = {}
        # with open("~/database_records.json", "r") as f:
        #     self.database_records = json.load(f)

    def get_metadata(self, page_id: str) -> dict:
        """Get page metadata as json."""
        return self.transformer.forward([self.client.pages.retrieve(page_id=page_id)])[0]

    def get_recent_pages(self) -> List[Dict[str, Any]]:
        """Get Recent Pages via Search Query.

        Returns:
            List[Dict[str, Any]]: List of Recent Pages
        """
        payload = {
            "filter": {
                "value": "page",
                "property": "object",
            },
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time",
            },
        }
        return self.client.search(**payload).get("results")

    def get_recent_projects(self) -> List[Dict[str, Any]]:
        """Get Recent Projects via Search Query.

        Returns:
            List[Dict[str, Any]]: List of Recent Projects
        """
        payload = {
            "query": "project",
            "filter": {
                "value": "page",
                "property": "object",
            },
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time",
            },
        }
        return self.client.search(**payload).get("results")

    def get_blocks(self, block_id: int) -> List:
        """Get all page blocks as json. Recursively fetches descendants."""
        blocks = []
        results = paginate(self.client.blocks.children.list, block_id=block_id)
        for child in results:
            child["children"] = list(self.get_blocks(child["id"])) if child["has_children"] else []
            blocks.append(child)
        return list(self.transformer.forward(blocks))

    def get_database(self, database_id: str) -> List:
        """Fetch pages in database as json."""
        if self.filter:
            results = paginate(
                self.client.databases.query,
                database_id=database_id,
                filter=self.filter,
            )
        else:
            results = paginate(
                self.client.databases.query,
                database_id=database_id,
            )
        pages = [self.client.pages.retrieve(page_id=pg["id"]) for pg in results]
        return list(self.transformer.forward(pages))


# class NotionDatabase:
#     def __init__(self, token: str):
#         self.client = Client(auth=token)

#     def get_databases(self) -> List[Database]:
#         """Get all databases."""
#         return [Database.from_dict(db) for db in self.client.databases.list()]

#     def get_database(self, database_id: str) -> Database:
#         """Get a database."""
#         return Database.from_dict(self.client.databases.retrieve(database_id=database_id))

#     def get_pages(self, database_id: str) -> List[Page]:
#         """Get all pages in a database."""
#         return [Page.from_dict(pg) for pg in self.client.databases.query(database_id=database_id).get("results")]

#     def get_page(self, page_id: str) -> Page:
#         """Get a page."""
#         return Page.from_dict(self.client.pages.retrieve(page_id=page_id))


class NotionPage:
    def __init__(self, token: str, page_id: str):
        self.client = Client(auth=token)
        self.page_id = page_id
        self.page = self.client.pages.retrieve(page_id=page_id)

    def get_page(self) -> Page:
        """Get a page."""
        return Page.from_dict(self.page)

    def get_blocks(self) -> List[dict]:
        """Get all blocks in a page."""
        return self.client.blocks.children.list(block_id=self.page_id).get("results")

    def set_blocks(self, blocks: List[dict], clear: bool = False):
        """Set all blocks in a page."""
        if clear:
            self.client.blocks.children.append(block_id=self.page_id, children=blocks)
        else:
            self.client.blocks.children.update(block_id=self.page_id, children=blocks)

    def add_page(self, page: Page):
        """Add a page to the current page."""
        self.client.blocks.children.append(block_id=self.page_id, children=[page.to_dict()])

    def add_database(self, database: Database):
        """Add a database to the current page."""
        self.client.databases.create(parent={"page_id": self.page_id}, database=database.to_dict())
