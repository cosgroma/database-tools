from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from bson import ObjectId
from pydantic import Field

from .common import Element


class DocBlockElementType(str, Enum):
    TEXT = "text"
    EMPHASIS = "emphasis"
    STRONG = "strong"
    LINK = "link"
    IMAGE = "image"
    CODESPAN = "codespan"
    LINE_BREAK = "linebreak"
    SOFT_BREAK = "softbreak"
    BLANK_LINE = "blank_line"
    INLINE_HTML = "inline_html"
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    THEMATIC_BREAK = "thematic_break"
    BLOCK_TEXT = "block_text"
    BLOCK_CODE = "block_code"
    BLOCK_QUOTE = "block_quote"
    BLOCK_HTML = "block_html"

    LIST_ITEM = "list_item"
    LIST = "list"

    TABLE = "table"
    TABLE_HEAD = "table_head"
    TABLE_BODY = "table_body"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"

    RESOURCE_REFERENCE = "resource_reference"


class DocBlockElement(Element):
    """
    1. Store block content
    """

    type: DocBlockElementType
    block_content: Optional[str] = Field(None, description="The content stored in this block")
    block_attr: Optional[Dict[str, Any]] = Field(None, description="Document block specific attributes")
    children: Optional[List[ObjectId]] = Field([], description="Ordered list of children blocks")
    export_id: Optional[ObjectId] = Field(None, description="For pages that are from an export which get assigned an ID.")


class PageTypes(str, Enum):
    PAGE = "page"
    FOLDER = "folder"
    EXPORT = "export"


class PageElement(Element):
    type: PageTypes
    children: Optional[List[ObjectId]] = Field([], description="An ordered list of id's to children DocBlocks")
    sub_folders: Optional[List[ObjectId]] = Field([], description="")
    export_name: Optional[str] = Field(None, description="")
    export_id: Optional[ObjectId] = Field(None, description="")
    relative_path: Optional[str] = Field(None, description="")

    confluence_space_key: Optional[str] = Field(None, description="The space name of the item in confluence")
    confluence_page_name: Optional[str] = Field(None, description="The aliased name on confluence")
    confluence_page_id: Optional[str] = Field(None, description="The page id of the confluence page")
