from pprint import pprint

from databasetools.managers.docs_manager import DocManager
from databasetools.models.block_model import DocBlockElement, DocBlockElementType
from typing import Dict, List, Any, Callable
from bson import ObjectId

def check_type(block: DocBlockElement, expected_type: DocBlockElementType):
        if block.type != expected_type:
            raise InvalidBlockInput(block.type, expected_type)

class DocBlock2Md:
    def __init__(self):
        self._default_func_list = {
            # Atomic types, No Children
            DocBlockElementType.TEXT: self._text,
            DocBlockElementType.HEADING: self._heading,
            DocBlockElementType.BLOCK_CODE: self._block_code,
            DocBlockElementType.CODESPAN: self._codespan,
            DocBlockElementType.THEMATIC_BREAK: self._thematic_break,
            
            # Derived types, from atomic types
            DocBlockElementType.IMAGE: self._image, # Text
            DocBlockElementType.LINK: self._link, # Text, Strong, Emphasis, Codespan, Image
            DocBlockElementType.PARAGRAPH: self._paragraph, # Text, Emphasis, Strong, Link, Image, Codespan, Linebreak, Softbreak
            DocBlockElementType.BLOCK_TEXT: self._block_text, # Text, Emphasis, Strong, Link, Image, Codespan, Linebreak, Softbreak
            DocBlockElementType.BLOCK_QUOTE: self._block_quote, # Text, Emphasis, Strong, Link, Image, Codespan, Block Code, Linebreak, Softbreak, Paragraph
            DocBlockElementType.LIST_ITEM: self._list_item,
            DocBlockElementType.LIST: self._list,
            
            DocBlockElementType.TABLE: self._table,
            DocBlockElementType.TABLE_HEAD: self._table_head,
            DocBlockElementType.TABLE_BODY: self._table_body,
            DocBlockElementType.TABLE_ROW: self._table_row,
            DocBlockElementType.TABLE_CELL: self._table_cell,
            
            # HTML types
            DocBlockElementType.BLOCK_HTML: self._block_html
        }
        self.__block_cache = {}
        
    @property
    def _block_cache(self):
        return self.__block_cache.copy()
    
    @_block_cache.setter
    def _block_cache(self, block_list: List[DocBlockElement]):
        new_list = block_list
        for block in new_list:
            block = block.model_copy()
            self.__block_cache += {block.id: block}
        
    @classmethod
    def docblocks2md(cls, block_list: List[DocBlockElement]) -> str:
        converter = cls()
        converter._block_cache = block_list
        return converter.stringify()
    
    def stringify(self) -> str:
        '''
        Stringifies what is in the cache
        '''
    
    def make_string_from_id(self, id_list: List[ObjectId]) -> str:
        pass
    
    def _text(self, block: DocBlockElement) -> str:
        check_type(block, DocBlockElementType.TEXT)
        return block.block_content
    
    def _heading(self, block: DocBlockElement) -> str:
        check_type(block, DocBlockElementType.HEADING)
        level = block.block_attr["level"]
        out = "#" * level
        out += " " + block.block_content
        return out
    
    def _block_code(self, block: DocBlockElement) -> str:
        check_type(block, DocBlockElementType.BLOCK_CODE)
        lang = block.block_attr.get("language")
        out = "```" + ("" if not lang else lang) + "\n"
        out += block.block_content
        out += "```"
        return out
            
    def _codespan(self, block: DocBlockElement) -> str:
        check_type(block, DocBlockElementType.CODESPAN)
        return "`" + block.block_content + "`"

    def _thematic_break(self, _) -> str:
        return "---"
    
    def _image(self, block: DocBlockElement) -> str: # Need to add support for finding resources
        check_type(block, DocBlockElementType.IMAGE)
        text = block.block_content
        url = block.block_attr["url"]
        return f"![{text}]({url})"
    
    def _link(self, block: DocBlockElement) -> str:
        check_type(block, DocBlockElementType.LINK)
        url = block.block_attr["url"]
        text = self.docblock2md(block.children)
        return f"[{text}]({url})"
    
    def _paragraph(self, block: DocBlockElement) -> str:
        pass
    
    def _block_text(self, block: DocBlockElement) -> str:
        pass
    
    def _block_quote(self, block: DocBlockElement) -> str:
        pass
    
    def _list_item(self, block: DocBlockElement) -> str:
        pass
    
    def _list(self, block: DocBlockElement) -> str:
        pass
    
    def _table(self, block: DocBlockElement) -> str:
        pass
    
    def _table_head(self, block: DocBlockElement) -> str:
        pass
    
    def _table_body(self, block: DocBlockElement) -> str:
        pass
    
    def _table_row(self, block: DocBlockElement) -> str:
        pass
    
    def _table_cell(self, block: DocBlockElement) -> str:
        pass
    
    def _block_html(self, block: DocBlockElement) -> str:
        pass

    
class InvalidBlockInput(Exception):
    def __init__(self, type: str, expected_type: str) -> None:
        output = f"Expected, {expected_type}, but got {type} instead!"
        super().__init__(output)