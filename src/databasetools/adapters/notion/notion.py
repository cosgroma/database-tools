"""
This module provides tools to interact with the Notion API, enabling data management and export for pages and databases.

### Key Components
1. **NotionClient**:
   - Primary client for interacting with Notion pages and databases.
   - Provides methods to fetch page metadata, recent pages/projects, page blocks, and databases.

2. **NotionDownloader**:
   - Uses NotionClient to download Notion pages and databases.
   - Supports recursive download of page blocks and maintains last-edited timestamps.
   - Allows saving pages as JSON files locally.

3. **NotionExporter**:
   - Combines the functionality of NotionDownloader and JsonToMdConverter.
   - Enables exporting pages or entire databases from Notion to markdown.

4. **NotionPage**:
   - Represents a Notion page with methods to manage blocks and child pages.
   - Supports adding, removing, and clearing blocks as well as child pages/databases.

5. **NotionDatabase**:
   - Represents a Notion database.
   - Supports fetching, adding, and removing pages within the database.

6. **NotionIO**:
   - Handles loading and saving Notion pages and blocks to/from JSON files.

7. **LastEditedToDateTime**:
   - Helper class for converting 'last_edited_time' values to datetime objects.

### Usage Examples
- **Downloading Pages**:
    ```python
    downloader = NotionDownloader(token="your-integration-token")
    downloader.download_url("https://www.notion.so/some-page-url")
    ```
- **Exporting to Markdown**:
    ```python
    exporter = NotionExporter(token="your-integration-token")
    exporter.export_url("https://www.notion.so/some-page-url", md_dir="./md_output")
    ```
"""

import json
import os
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from fuzzywuzzy import fuzz
from notion_client import Client
from notion_client.helpers import iterate_paginated_api as paginate
from notion_objects import Database
from notion_objects import NotionObject
from notion_objects import Page

# import networkx as nx
# import matplotlib.pyplot as plt
# G = nx.DiGraph()
from .json2md import JsonToMdConverter
from .utils import find_title_prop
from .utils import get_title_content
from .utils import logger
from .utils import normalize_id
from .utils import slugify

NOTION_API_KEY = os.getenv("NOTION_API_KEY", None)


class BaseTransformer(ABC):
    key: str = None

    @abstractmethod
    def forward(self, blocks: List[dict]) -> List[dict]: ...

    @abstractmethod
    def reverse(self, o: Any) -> Union[None, str]: ...


class LastEditedToDateTime(BaseTransformer):
    key = "last_edited_time"
    key_type = datetime

    def forward(self, blocks) -> List:
        """Convert last_edited_time to datetime object.
        Args:
            blocks (List[dict]): List of blocks

        Returns:
            List: List of blocks with last_edited_time as datetime object
        """
        key = self.key
        return [
            {
                **block,
                key: datetime.fromisoformat(block[key][:-1]),
                "id": normalize_id(block["id"]),
            }
            for block in blocks
        ]

    def reverse(self, o: Any) -> Union[None, str]:
        """Convert datetime object to string.
        Args:
            o (Any): Object
        Returns:
            Union[None, str]: String representation of datetime object
        """
        if isinstance(o, datetime):
            return o.isoformat() + "Z"


class NotionIO:
    def __init__(self, transformer: BaseTransformer):
        self.transformer = transformer

    def load(self, path: Union[str, Path]) -> List[dict]:
        """Load blocks from json file."""
        if Path(path).exists():
            with Path.open(path) as f:
                return self.transformer.forward(json.load(f))
        return []

    def save(self, blocks: List[dict], path: Union[str, Path], overwrite: bool = False):
        """Dump blocks to json file."""
        if not blocks:
            raise ValueError("No blocks to save.")
        if not isinstance(blocks, list):
            raise ValueError("Blocks must be a list.")
        if not isinstance(blocks[0], dict):
            raise ValueError("Blocks must be a list of dictionaries.")
        if not path:
            raise ValueError("No path provided.")
        path = Path(path)
        if path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {path}")

        with Path.open(path, "w") as f:
            json.dump(blocks, f, default=self.transformer.reverse, indent=4)


class NotionClient:
    """
    A client for interacting with Notion pages and databases.

    This class provides methods to retrieve metadata, recent pages, projects, page blocks, and databases from the Notion API.

    Attributes:
        token (str): The authentication token for accessing the Notion API.
        filter (Optional[dict]): Optional filter for database queries.
        client (Client): The Notion client object.
        transformer (LastEditedToDateTime): Utility for transforming date-time fields.

    Methods:
        get_metadata(page_id: str) -> Dict[str, Any]:
            Retrieves metadata of a specific page.

        get_recent_pages() -> List[Dict[str, Any]]:
            Retrieves a list of recent pages via a search query.

        get_recent_projects() -> List[Dict[str, Any]]:
            Retrieves a list of recent projects via a search query.

        get_blocks(block_id: int) -> List:
            Fetches all page blocks and their descendants recursively.

        get_database(database_id: str) -> List:
            Fetches pages within a specified database as JSON.

    Example Usage:
    --------------
    ```python
    client = NotionClient(token="your-notion-api-token")

    # Retrieve metadata for a specific page
    page_metadata = client.get_metadata(page_id="your-page-id")

    # Fetch recent pages
    recent_pages = client.get_recent_pages()

    # Fetch recent projects
    recent_projects = client.get_recent_projects()

    # Retrieve all blocks of a specific page
    blocks = client.get_blocks(block_id="your-block-id")

    # Retrieve pages in a specific database
    database_pages = client.get_database(database_id="your-database-id")
    ```
    """

    def __init__(self, token: str, transformer: LastEditedToDateTime = None, filter: Optional[dict] = None):
        self.token = token
        self.filter = filter
        self.client = Client(auth=token)
        self.transformer = transformer if transformer else LastEditedToDateTime()

    def get_metadata(self, page_id: str) -> Dict[str, Any]:
        """Get page metadata.

        Args:
            page_id (str): Page ID

        Returns:
            Dict[str, Any]: Page Metadata
        """
        return self.transformer.forward([self.client.pages.retrieve(page_id=page_id)])[0]

    def get_recent_pages(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
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
        if query:
            payload["query"] = query

        return self.client.search(**payload).get("results")

    def get_blocks(self, block_id: int) -> List:
        """Get all page blocks as json. Recursively fetches descendants.

        Args:
            block_id (int): Block ID

        Returns:
            List: List of page blocks
        """
        blocks = []
        results = paginate(self.client.blocks.children.list, block_id=block_id)
        for child in results:
            try:
                child["children"] = list(self.get_blocks(child["id"])) if child["has_children"] else []
                blocks.append(child)
            except Exception as e:
                logger.error(f"Error: {e}")

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


class NotionDownloader:
    """
    Downloads Notion pages and databases as JSON files.

    This class leverages the `NotionClient` to download pages and databases from the Notion API. It can recursively download page blocks and maintains metadata like last-edited timestamps. The downloaded data can be saved to a specified directory for offline analysis or further processing.

    Attributes:
        transformer (LastEditedToDateTime): Utility to convert date-time fields.
        notion (NotionClient): The main client instance to interact with Notion.
        io (NotionIO): Handles loading and saving JSON files.

    Methods:
        download_url(url: str, out_dir: Union[str, Path] = "./json"):
            Downloads the Notion page or database from a URL and saves it as JSON.

        download_page(page_id: str, out_path: Union[str, Path] = "./json", fetch_metadata: bool = True):
            Downloads a specific Notion page and its blocks. Metadata is optionally fetched and saved.

        download_database(database_id: str, out_dir: Union[str, Path] = "./json"):
            Downloads all pages and data from a specified Notion database.

    Example Usage:
    --------------
    ```python
    # Initialize the downloader with your Notion API token
    downloader = NotionDownloader(token="your-notion-api-token")

    # Download a Notion page by URL
    downloader.download_url("https://www.notion.so/some-page-url", out_dir="./json_pages")

    # Download a specific page by ID
    downloader.download_page(page_id="your-page-id", out_path="./json_pages/page.json")

    # Download all pages in a database
    downloader.download_database(database_id="your-database-id", out_dir="./json_database")
    ```
    """

    def __init__(self, token: str, filter: Optional[str] = None):
        self.transformer = LastEditedToDateTime()
        self.io = NotionIO(self.transformer)
        self.notion = NotionClient(token=token, transformer=self.transformer, filter=filter)

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


class NotionExporter:
    def __init__(self, token: str, strip_meta_chars: Optional[str] = None, extension: str = "md", filter: Optional[dict] = None):
        self.downloader = NotionDownloader(token, filter)
        self.converter = JsonToMdConverter(strip_meta_chars=strip_meta_chars, extension=extension)

    def export_url(self, url: str, json_dir: Union[str, Path] = "./json", md_dir: Union[str, Path] = "./md") -> Path:
        """Export the notion page or database."""
        self.downloader.download_url(url, json_dir)
        return self.converter.convert(json_dir, md_dir)

    def export_database(self, database_id: str, json_dir: Union[str, Path] = "./json", md_dir: Union[str, Path] = "./md") -> Path:
        """Export the notion database and associated pages."""
        self.downloader.download_database(database_id, json_dir)
        return self.converter.convert(json_dir, md_dir)

    def export_page(self, page_id: str, json_dir: Union[str, Path] = "./json", md_dir: Union[str, Path] = "./md"):
        """Export the notion page."""
        json_dir_path = Path(json_dir)
        self.downloader.download_page(page_id, json_dir_path / f"{page_id}.json")
        return self.converter.convert(json_dir, md_dir)


class NotionPage:
    def __init__(
        self,
        token: Optional[str] = None,
        page_id: Optional[str] = None,
        parent: Optional["NotionPage"] = None,
        load: bool = False,
        recursive: bool = False,
    ):
        if NOTION_API_KEY:
            token = NOTION_API_KEY
        if token is None:
            raise ValueError("No token provided.")

        self.token = token
        self.n_client = NotionClient(token)

        self.page_id = page_id
        self.parent = parent
        self.title = None

        self.blocks: List[dict] = []
        self.children: List[Union["NotionPage", "NotionDatabase"]] = []
        self.child_pages: List["NotionPage"] = []
        self.child_databases: List["NotionDatabase"] = []

        self.page_results: dict = {}
        self.page = None
        self.parent = None

        self.get_page()

        if load:
            self.get_blocks()

        if recursive:
            self.get_children(recursive=recursive)

        self.local_dir = Path.cwd()
        self.file_path = None

        if self.title:
            self.basename = slugify(self.title)

    def set_local_dir(self, local_dir: Union[str, Path]):
        """Set the local directory for saving files.

        Args:
            local_dir (Union[str, Path]): Local Directory

        """
        self.local_dir = Path(local_dir)

    def get_file_path(self) -> Path:
        """Get the file path for saving the page.

        Returns:
            Path: File Path
        """
        return self.file_path

    def set_file_path(self, file_name: Union[str, Path]):
        self.file_path = self.local_dir / file_name
        self.file_type = self.file_path.suffix[1:]

    def save(self, type: str = "json", recursive: bool = False, file_name: Optional[str] = None, parent_name: Optional[str] = None) -> Path:
        """Save the page as a file.

        Args:
            type (str, optional): File Type. Defaults to "json".
            recursive (bool, optional): Save recursively. Defaults to False.
            file_name (Optional[str], optional): File Name. Defaults to None.
            parent_name (Optional[str], optional): Parent Name. Defaults to None.

        Returns:
            Path: File Path
        """
        if self.page_id is None:
            raise ValueError("Page ID is not provided.")
        self.transformer = LastEditedToDateTime()
        self.io = NotionIO(self.transformer)
        metadata = self.n_client.get_metadata(self.page_id)
        metadata_filename = self.local_dir / "page_metadata.json"
        self.io.save([metadata], metadata_filename)
        logger.info(f"Saved metadata to {metadata_filename}")

        if len(self.blocks) == 0:
            self.get_blocks()
            if len(self.blocks) == 0:
                raise ValueError("No blocks found.")

        if file_name is not None:
            self.set_file_path(file_name)

        if self.file_path is None:
            file_name = f"{slugify(self.title)}.{type}"
            self.set_file_path(file_name)

        #  def get_post_metadata(self, post):
        # converter = JsonToMd(config={"apply_list": {"delimiter": ","}})
        # return {key: self.get_key(converter.json2md(value)) for key, value in post["properties"].items() if converter.json2md(value)}
        # markdown = JsonToMd(metadata).page2md(blocks)
        self.io.save(self.blocks, self.file_path)
        if recursive:
            for page in self.child_pages:
                page.save(type=type, recursive=True)

        logger.info(f"Saved blocks to {self.file_path}")
        return self.file_path

    def get_page(self, force: bool = False) -> Tuple[Page, dict]:
        """Get a page."""
        if self.page_id is None:
            raise ValueError("Page ID is not provided.")
        if force or not self.page:
            self.page_results = self.n_client.client.pages.retrieve(page_id=self.page_id)
            self.page = Page(self.page_results)

            if self.page_results["parent"]["type"] != "database_id":
                title_prop = "title"
            else:
                title_prop = find_title_prop(self.page_results["properties"])
            # get_title_content
            self.title = get_title_content(self.page_results["properties"][title_prop])

        return self.page, self.page_results

    def get_blocks(self, force: bool = False) -> List[dict]:
        """Get all blocks in a page.

        Args:
            force (bool, optional): Force Refresh. Defaults to False.

        Returns:
            List[dict]: List of Blocks
        """
        if force or not self.blocks:
            self.blocks = self.n_client.get_blocks(self.page_id)
        return self.blocks

    def set_blocks(self, blocks: List[dict], clear: bool = False):
        """Set all blocks in a page.

        Args:
            blocks (List[dict]): List of Blocks
            clear (bool, optional): Clear Existing Blocks. Defaults to False.


        """
        if clear:
            self.clear_blocks()
        if not blocks:
            raise ValueError("No blocks provided.")
        if not isinstance(blocks, list):
            raise ValueError("Blocks must be a list.")
        if len(blocks) == 0:
            raise ValueError("Blocks must not be empty.")
        if not isinstance(blocks[0], dict):
            raise ValueError("Blocks must be a list of dictionaries.")

        self.n_client.client.blocks.children.append(block_id=self.page_id, children=blocks)

    def clear_blocks(self):
        """Clear all blocks in a page."""

        blocks = self.get_blocks(force=True)
        for block in blocks:
            self.n_client.client.blocks.delete(block_id=block["id"])

    def add_page(self, title: str) -> "NotionPage":
        """Add a page to the current page.

        Args:
            title (str): Page Title

        Returns:
            NotionPage: Notion Page
        """
        page = self.n_client.client.pages.create(
            parent={"page_id": self.page_id},
            properties={"title": [{"text": {"content": title}}]},
        )
        return NotionPage(token=self.n_client.token, page_id=page["id"], load=False)

    def add_database(self, title: str) -> "NotionDatabase":
        """Add a database to the current page."""
        database = self.n_client.client.databases.create(
            parent={"page_id": self.page_id}, title=[{"text": {"content": title}}], properties={"Name": {"title": {}}}
        )
        return NotionDatabase(token=self.n_client.token, database_id=database["id"])

    def get_children(self, force: bool = False, recursive: bool = False) -> List[Union["NotionPage", "NotionDatabase"]]:
        """Get children of a page."""
        if force or not self.children:
            try:
                blocks = self.get_blocks()
                for block in blocks:
                    if block["type"] == "child_page":
                        self.children.append(NotionPage(token=self.n_client.token, page_id=block["id"], load=False, recursive=recursive))
                    elif block["type"] == "child_database":
                        self.children.append(NotionDatabase(token=self.n_client.token, database_id=block["id"]))
            except Exception as e:
                logger.error(f"Error: {e}")
        return self.children

    def get_child_pages(self, force: bool = False) -> List["NotionPage"]:
        """Get Child Pages.

        Args:
            page_id (str): Page ID

        Returns:
            List[dict]: List of Child Pages
        """

        if force or not self.child_pages:
            try:
                blocks = self.get_blocks()
                for block in blocks:
                    if block["type"] == "child_page":
                        self.child_pages.append(NotionPage(token=self.n_client.token, page_id=block["id"], load=False))
            except Exception as e:
                logger.error(f"Error: {e}")
        return self.child_pages

    def get_child_databases(self, force: bool = False) -> List["NotionDatabase"]:
        """Get Child Databases.

        Args:
            force (bool, optional): Force Refresh. Defaults to False.

        Returns:
            List[dict]: List of Child Databases
        """
        if force or not self.child_databases:
            blocks = self.get_blocks()
            for block in blocks:
                if block["type"] == "child_database":
                    self.child_databases.append(NotionDatabase(token=self.n_client.token, database_id=block["id"]))
        return self.child_databases

    def delete_child_pages(self):
        """Delete Child Pages."""
        for page in self.child_pages:
            self.n_client.client.blocks.delete(block_id=page.page_id)
            self.child_pages.remove(page)

    def delete_page(self):
        """Delete Page."""
        self.n_client.client.blocks.delete(block_id=self.page_id)

    def __repr__(self):
        return f"NotionPage(title={self.title}, page_id={self.page_id})"

    def info(self):
        return {
            "title": self.title,
            "page_id": self.page_id,
            "parent": self.parent,
            "blocks": self.blocks,
            "children": self.children,
            "child_pages": self.child_pages,
            "child_databases": self.child_databases,
            "local_dir": self.local_dir,
        }


def create_code_name(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")


def generate_model_class_code(class_name: str, properties: Dict[str, Any], file_path: Optional[Union[str, Path]] = None) -> str:
    # remove spaces and special characters from class name
    class_name = create_code_name(class_name)
    class_code = f"class {class_name}(NotionObject):\n"
    property_map = {
        "title": "TitleText",
        "rich_text": "Text",
        "multi_select": "MultiSelect",
        "status": "Status",
        "checkbox": "Checkbox",
        "created_time": "CreatedTime",
    }

    for prop_name, prop_info in properties.items():
        prop_type = property_map.get(prop_info["type"], "Text")  # Default to Text if type is not mapped
        class_code += f"    {create_code_name(prop_name.lower())} = {prop_type}('{prop_name}')\n"

    if not file_path:
        # print(class_code)
        file_path = Path.cwd() / f"{class_name}.py"

    with Path.open(file_path, "w") as f:
        f.write(class_code)
    return class_code


DATABASE_PROPERTIES = {
    "number": {},
    "formula": {},
    "select": {},
    "multi_select": {},
    "status": {},
    "relation": {},
    "rollup": {},
    "unique_id": {},
    "title": {},
    "rich_text": {},
    "url": {},
    "people": {},
    "files": {},
    "email": {},
    "phone_number": {},
    "date": {},
    "checkbox": {},
    "created_by": {},
    "created_time": {},
    "last_edited_by": {},
    "last_edited_time": {},
    "button": {},
    "location": {},
    "verification": {},
    "last_visited_time": {},
    "name": {},
}

# "parent": {
# "type": "page_id",
# "page_id": "7f64948c-b0c0-46e4-95c4-fb7e93813488"
# },
# "parent": {
# "type": "workspace",
# "workspace": true
# },
# "parent": {
# "type": "block_id",
# "block_id": "1c8561b8-1d2e-41f5-b11c-f9f0d5096b16"
# },


class NotionDatabase:
    """Notion Database Class

    Attributes:

        token (str): The authentication token for accessing the Notion API.
        database_id (str): The ID of the Notion database.
        DataClass (Optional[NotionObject]): The custom data class for database entries.
        n_client (NotionClient): The Notion client object.
        database (Database): The Notion database object.
        properties (Dict[str, Any]): The properties of the database.
        pages (List[NotionPage]): The list of pages in the database.
        parent (Optional[NotionPage]): The parent page of the database.
        custom_data_class (bool): Flag to indicate if a custom data class is used.

    Methods:

        set_parent(parent: NotionPage): Set the parent page of the database.
        set_parent_by_id(parent_id: str): Set the parent page by ID.
        get_parent() -> NotionPage: Get the parent page.
        get_parent_id() -> str: Get the parent page ID.
        get_property_map(source_properties: List[str], threshold: int = 80) -> Dict[str, str]: Get the property mappings.
        load_from_json(json_path: Union[str, Path], database_id: str, DataClass: Optional[NotionObject] = None, create_properties: bool = False, force: bool = False): Load data from JSON file.
        load_database(database_id: str): Load the database.
        get_properties() -> Dict[str, Any]: Get the database properties.
        add_property(prop_name: str, prop_type: Optional[str] = "rich_text", prop_info: Optional[Dict[str, Any]] = None): Add a property to the database.
        remove_property(prop_name: str): Remove a property from the database.
        get_children(force: bool = False) -> List[NotionPage]: Get the children of the database.
        get_pages(force: bool = False) -> List[NotionPage]: Get the pages in the database.
        create(properties: Optional[Dict[str, Any]] = None, obj: Optional[NotionObject] = None) -> NotionObject: Create a database entry.
        check_if_exists(title: str) -> bool: Check if a database entry exists.

    Example Usage:

        ```python
        database = NotionDatabase(token="your-integration-token", database_id="your-database-id")
        database.load_database(database_id="your-database-id")
        database.get_properties()
        database.add_property("Name", "rich_text")
        database.remove_property("Name")
        database.get_children()
        database.get_pages()
        database.create({"Name": "John Doe"})
        database.check_if_exists("John Doe")
        ```
    """

    def __init__(self, token: Optional[str] = None, database_id: Optional[str] = None, DataClass: Optional[NotionObject] = None):
        if NOTION_API_KEY:
            token = NOTION_API_KEY
        if token is None:
            raise ValueError("No token provided.")
        self.token = token
        self.n_client = NotionClient(token=token)
        self.database_id = database_id

        if DataClass is None:
            self.DataClass = Page
            self.custom_data_class = False
        else:
            self.custom_data_class = True
            self.DataClass = DataClass

        if not issubclass(self.DataClass, NotionObject):
            raise ValueError("DataClass must be a subclass of NotionObject.")

        self.database: Optional[Database[self.DataClass]] = None
        self.properties: Dict[str, Any] = {}
        self.pages: List[NotionPage] = []
        self.parent: Optional[NotionPage] = None

        if self.database_id is not None:
            self.load_database(database_id)

    def set_parent(self, parent: NotionPage):
        self.parent = parent

    def set_parent_by_id(self, parent_id: str):
        self.parent = NotionPage(token=self.token, page_id=parent_id, load=False)

    def get_parent(self) -> NotionPage:
        return self.parent

    def get_parent_id(self) -> str:
        return self.parent.page_id

    def get_property_map(self, source_properties: List[str], threshold: int = 80) -> Dict[str, str]:
        mappings = {}
        db_prop_names = [prop["name"] for prop in self.get_properties().values()]

        for src_property in source_properties:
            best_match = None
            best_score = 0
            for prop in db_prop_names:
                score = fuzz.ratio(src_property.lower(), prop.lower())
                if score > best_score:
                    best_score = score
                    best_match = prop
            if best_score > threshold:  # Threshold for fuzzy match
                mappings[src_property] = best_match
                db_prop_names.remove(best_match)

        return mappings

    def load_from_json(
        self,
        json_path: Union[str, Path],
        database_id: str,
        DataClass: Optional[NotionObject] = None,
        create_properties: bool = False,
        force: bool = False,
    ):
        self.database_id = database_id
        self.DataClass = DataClass
        self.load_database(database_id)

        with Path.open(json_path) as f:
            records: List[Dict[str, Any]] = json.load(f)

        # filename = Path(json_path).stem
        # print(filename)
        record = records[0]
        properties = record.keys()
        # generate_model_class_code(filename, properties, file_path=None)

        db_prop_names = [prop["name"].lower() for prop in self.get_properties().values()]
        print(f"Database properties: {db_prop_names}")
        properties_map = self.get_property_map(properties, threshold=80)
        print(f"Property mappings: {properties_map}")
        for prop in properties:
            if prop in properties_map and properties_map[prop] in db_prop_names:
                print(f"Mapping '{prop}' to '{properties_map[prop]}'")
                continue
            else:
                logger.warning(f"Property '{prop}' not found in database properties.")
                if create_properties:
                    prop_type = "rich_text"
                    if isinstance(record[prop], str):
                        prop_type = "rich_text"
                    elif isinstance(record[prop], int):
                        prop_type = "number"
                    elif isinstance(record[prop], bool):
                        prop_type = "checkbox"
                    elif isinstance(record[prop], datetime):
                        prop_type = "date"
                    elif isinstance(record[prop], list):
                        prop_type = "multi_select"
                    logger.info(f"Creating property '{prop}' with type '{prop_type}'")
                    self.add_property(prop, prop_type)

        for record in records:
            update_record = {}
            for prop, value in record.items():
                if prop in properties_map:
                    update_record[properties_map[prop]] = value
                    print(f"Mapping '{prop}' to '{properties_map[prop]}'")
                else:
                    print(f"Property '{prop}' not found in database properties.")

            if update_record:
                print(f"Creating record: {update_record}")
                self.create(update_record)

    def load_database(self, database_id: str):
        """Load the database.

        Args:
            database_id (str): Database ID
        """
        self.database_id = database_id

        try:
            self.database_info: Dict[str, Any] = self.n_client.client.databases.retrieve(database_id=database_id)
            self.title = self.database_info["title"]
            parent_type = self.database_info["parent"]["type"]
            if parent_type == "page_id":
                self.parent = NotionPage(token=self.token, page_id=self.database_info["parent"][parent_type], load=False)
        except Exception as e:
            raise ValueError(f"Database with ID '{database_id}' not found.") from e

        self.database: Database[self.DataClass] = Database(self.DataClass, database_id=database_id, client=self.n_client.client)

        if self.database is None:
            raise ValueError(f"Fail to load Database on valid ID '{database_id}'.")

        self.properties = self.database_info["properties"]

        for page in self.database:
            self.pages.append(NotionPage(token=self.token, page_id=page.id, load=False))

    def get_properties(self) -> Dict[str, Any]:
        """Get the database properties.

        Returns:
            Dict[str, Any]: Database Properties
        """
        self.database_info: Dict[str, Any] = self.n_client.client.databases.retrieve(database_id=self.database_id)
        self.properties = self.database_info["properties"]
        return self.properties

    # "Tasks": {
    #     "id": "%3AVpi",
    #     "name": "Tasks",
    #     "type": "relation",
    #     "relation": {
    #         "database_id": "ac1f2415-2252-4961-b983-b28817e0ef7a",
    #         "type": "single_property",
    #         "single_property": {}
    #     }
    # },
    def add_property(self, prop_name: str, prop_type: Optional[str] = "rich_text", prop_info: Optional[Dict[str, Any]] = None):
        if prop_type not in DATABASE_PROPERTIES:
            raise ValueError(f"Invalid property type '{prop_type}'.")
        if prop_info is None:
            prop_info = {}
        properties_update = {
            "type": prop_type,
            prop_type: prop_info,
        }
        self.n_client.client.databases.update(self.database_id, properties={prop_name: properties_update})

    def remove_property(self, prop_name: str):
        try:
            self.n_client.client.databases.update(self.database_id, properties={prop_name: None})
        except Exception:
            logger.error(f"Failed to remove property '{prop_name}' from database '{self.database_id}'.")

    def get_children(self, force: bool = False) -> List[NotionPage]:
        return self.get_pages(force=force)

    def get_pages(self, force: bool = False) -> List[NotionPage]:
        """Get Pages."""
        if force or not self.pages:
            for page in self.database:
                self.pages.append(NotionPage(token=self.n_client.token, page_id=page.id, load=False))
        return self.pages

    # def new(self, parent: Optional[NotionPage] = None, **kwargs) -> NotionObject:
    #     """Create a new Database Entry."""
    #     if parent is None and self.parent is None:
    #         raise ValueError("Parent NotionPage must be provided.")
    #     if parent is None:
    #         parent = self.parent
    #     return self.database.new(parent=parent.page_id, **kwargs)
    def check_if_exists(self, title: str) -> bool:
        """Check if Database Entry Exists."""
        for page in self.pages:
            if page.title == title:
                return True

    def create(self, properties: Optional[Dict[str, Any]] = None, obj: Optional[NotionObject] = None) -> NotionObject:
        """Create Database Entry."""
        if properties is None and obj is None:
            raise ValueError("Either properties or obj must be provided.")
        if properties is not None and obj is not None:
            raise ValueError("Only one of properties or obj can be provided.")
        # for prop_name, prop_info in properties.items():
        #     if prop_name not in self.database.properties:
        #         raise ValueError(f"Property '{prop_name}' not found in database properties.")

        if obj is not None:
            entry = obj
        else:
            entry = self.DataClass.new(**properties)

        # if self.check_if_exists(entry):
        #     logger.warning(f"Entry '{entry.ref}' already exists in database.")
        #     db_entry = next((page for page in self.pages if page.title == entry.ref), None)
        #     return db_entry

        db_entry = self.database.create(entry)
        self.pages.append(NotionPage(token=self.token, page_id=db_entry.id, load=False))
        return db_entry

    def read(self, entry_id: str) -> NotionObject:
        """Read Database Entry."""
        return self.database.find_by_id(entry_id)

    def update(self, entry: NotionObject, properties: Optional[Dict[str, Any]] = None) -> NotionObject:
        """Update Database Entry."""
        for k, v in properties.items():
            setattr(entry, k, v)
        self.database.update(entry)
        return entry

    def delete(self, entry: NotionObject):
        """Delete Database Entry."""
        self.n_client.client.blocks.delete(block_id=entry.id)
        self.pages.remove(entry)

    def delete_all(self):
        """Remove Pages."""
        for page in self.pages:
            self.n_client.client.blocks.delete(block_id=page.page_id)
            self.pages.remove(page)

    def __repr__(self):
        return f"NotionDatabase(title={self.database.title}, database_id={self.database.database_id})"

    def __iter__(self):
        return iter(self.database)

    def query(self, filter: Optional[dict] = None) -> List[NotionObject]:
        results = self.database.query(filter=filter)
        pages: List[NotionPage] = []
        for result in results:
            if isinstance(result, dict):
                pages.append(NotionPage(token=self.token, page_id=result["id"], load=False))
            else:
                print(f"result not dict: {type(result)}")

    def download_database(self, database_id: str, out_dir: Union[str, Path] = "./json"):
        """Download the notion database and associated pages."""
        # out_dir = Path(out_dir)
        # out_dir.mkdir(parents=True, exist_ok=True)
        # path = out_dir / "database.json"
        # prev = {pg["id"]: pg["last_edited_time"] for pg in self.io.load(path)}
        # pages = self.notion.get_database(database_id)  # download database
        # self.io.save(pages, path)

        # for cur in pages:  # download individual pages in database IF updated
        #     if prev.get(cur["id"], datetime(1, 1, 1, tzinfo=cur["last_edited_time"].tzinfo)) < cur["last_edited_time"]:
        #         self.download_page(cur["id"], out_dir / f"{cur['id']}.json", False)
        #         logger.info(f"Downloaded {cur['url']}")
