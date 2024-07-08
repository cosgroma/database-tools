

from typing import Optional, List, Dict, Any
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum


from .common import Element, Relationship

class DocBlockElementType(str, Enum):
    PAGE = "page"
    
    TEXT = "text"
    HEADING = "heading"
    BLOCK_CODE = "block_code"
    CODESPAN = "codespan"
    
    PARAGRAPH = "paragraph"
    BLOCK_TEXT = "block_text"
    LINK = "link"
    IMAGE = "image"
    BLOCK_QUOTE = "block_quote"
    LIST_ITEM = "list_item"
    LIST = "list"
    
    TABLE = "table"
    TABLE_HEAD = "table_head"
    TABLE_BODY = "table_body"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    
    THEMATIC_BREAK = "thematic_break"
    
    BLOCK_HTML = "block_html"

class DocBlockElement(Element):
    '''
        1. Store block content
    '''
    type: DocBlockElementType
    block_content: Optional[str] = Field(None, description="The content stored in this block")
    block_attr: Optional[Dict[str, Any]] = Field(None, description="Document block specific attributes")
    children: Optional[List[ObjectId]] = Field([], description="Ordered list of children blocks")

    
class PageElement(Element):
    '''
        Stores page metadata and is used to connect blocks to a page with PageRelationship
    '''
    pass

class BlockRelationship(Relationship):
    '''
        Should store intra-page relationships. eg. relationships between blocks
    '''
    pass

class PageRelationship(Relationship):
    '''
        Should store relationships between PageElement's to BlockElement's
    '''
    pass
