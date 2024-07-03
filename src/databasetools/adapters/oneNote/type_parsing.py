import mistune
import os
import frontmatter

from mistune.plugins.table import table
from typing import List, Dict, Any, Union, Tuple
from bson import ObjectId
from pprint import pprint
from pathlib import Path

from databasetools.models.block_model import DocBlockElement, DocBlockElementType

VALID_METADATA_VALUES = ["title", "id", "oneNoteId", "oneNotePath", "updated", "created"]

class OneNote_Export_to_DocBlock:
    def __init__(self):
        self.func_list = {
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
            DocBlockElementType.TABLE_CELL: self._table_cell
        }
        
    def type_exception_guard(self, check_token: Dict[str, Any], valid_types: List[str]): # FOR DEBUG
        for attribute in check_token:
            if attribute not in valid_types:
                raise TypeError("Extra attribute: " + attribute)
        
    def process_oneNote_page(self, file_path: Union[Path, str]) -> List[DocBlockElement]: # untested
        
        # "metadata": {
        #     "title": "Platform Library",
        #     "id": "27bd2f39d4cc4017b64bc9b26645e0d5",
        #     "oneNoteId": "{DDD92369-7933-0FFD-3970-C986A571D816}{1}{E1838393364313073899420146992507433720312551}",
        #     "oneNotePath": null,
        #     "updated": "2021-01-25 18:16:06-08:00",
        #     "created": "2021-01-25 18:15:19-08:00"
        # }
        file_path = Path(file_path)
        
        if file_path.suffix != ".md":
            raise TypeError(f"File: {file_path} does not have a .md extension.")
        elif not os.path.exists(file_path): 
            raise FileNotFoundError(f"The provided path: {file_path} does not exists.")
        elif not os.path.isfile(file_path):
            raise IsADirectoryError(f"The provided path: {file_path} is a directory. Use process_dir instead.")
        
        with open(file_path, "r") as f:
            metadata, md = frontmatter.parse(f.read())
            
        self.type_exception_guard(metadata, VALID_METADATA_VALUES)
            
        page_block_list = self.make_barebones_page(self.md_to_token(md))
        page_block = page_block_list[0]
        
        page_block.name = metadata.get("title")
        page_block.block_attr = {
            "oneNote_pageid": metadata.get("id"),
            "oneNoteId": metadata.get("oneNoteId"),
            "oneNote_created_at": metadata.get("created"),
            "oneNote_modified_at": metadata.get("updated"),
            "oneNote_path": metadata.get("oneNotePath"),
            "local_path": str(file_path),
            "file_name": os.path.splitext(os.path.basename(file_path))[0]
        }
        
        return page_block_list
        
    def md_to_token(self, raw_md: str) -> List[Dict[str, Any]]:
        '''
            Parses markdown into python tokens.
        '''
        remove_types = ["blank_line", None] # Add elements here if you need to trim the parsing
        bp = mistune.BlockParser(max_nested_level=10) # Instansiate a new block parser to a predefined max nesting level
        markdown = mistune.Markdown(renderer=None, block=bp, plugins=[table]) # renderer=None allows parsing to python tokens. Import other plugins as needed
        token_list = markdown(raw_md) 
        token_list = self._remove_bold_emphasis(token_list)
        return self._remove_elements_of_type(token_list, remove_types)
        
    def make_barebones_page(self, token_list: List[Dict[str, Any]]) -> List[DocBlockElement]:
        block_list = self.make_blocks(token_list)
        id_list = [block.id for block in block_list]
        block_list.insert(0, DocBlockElement(
            type="page",
            children=id_list
        ))
        return block_list
        
    def make_block(self, token: Dict[str, Any]):
        type = token["type"]
        if type in self.func_list:
            return self.func_list[type](token)
        raise KeyError(f"Invalid object type: {type}, in object: {token}")
    
    def make_blocks(self, token_list: List[Dict[str, Any]]) -> List[DocBlockElement]:
        block_list = []
        for item in token_list:
            new_block = self.make_block(item)
            if isinstance(new_block, list):
                block_list.extend(new_block)
            else:
                block_list.append(new_block)
        return block_list
    
    # Atomic types
    def _text(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(
            type="text",
            block_content=token["raw"]
        )

    def _heading(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(
            type="heading",
            block_attr={"level": token["attrs"]["level"]},
            block_content=token["children"][0]["raw"]
        )
    
    def _block_code(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(
            type="block_code",
            block_attr={
                "language": token.get("attrs").get("info")
            },
            block_content=token["raw"]
        )
        
    def _codespan(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(
            type="codespan",
            block_content=token["raw"]
        )
        
    def _thematic_break(self, _) -> DocBlockElement:
        return DocBlockElement(
            type="thematic_break"
        )
        
    # Derived types
    def _image(self, token: Dict[str, Any]) -> DocBlockElement:
        '''
            block_content: Contains all the raw alt text contained in the image.
            block_attr["url"]: Contains the url for the image.
        '''
        raw_text = self._simplify_raw_text(token.get("children"))
        if len(raw_text) > 1:
            raise TypeError("Unexpected syntax found in image feild: " + raw_text[1])
        return DocBlockElement(
            type="image",
            block_content=self._combine_text(token.get("children"))[0]["raw"],
            block_attr={
                "url": token["attrs"]["url"]
            }
        )
    
    def _link(self, token: Dict[str, Any]) -> List[DocBlockElement]: 
        '''
            block_content: Contains all raw text of the link.
            block_attr["url"]: Contains the urls of the link.
            children: Contains id's of text and image blocks that may be contained in the link. 
        '''
        block_list, raw_content, id_list = self._get_children_block_elements(token)
        
        block_list.insert(0, DocBlockElement(
            type="link",
            block_content=raw_content,
            block_attr={"url": token["attrs"]["url"]},
            children=id_list
        ))
        
        return block_list
        
    def _paragraph(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        '''
            block_content: All raw text of the paragraph block. ????? do i need this
            children: Id's of children blocks.
        '''
        block_list, raw_content, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type="paragraph",
            block_content=raw_content,
            children=id_list
        ))
        return block_list
    
    def _block_text(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        list = self._paragraph(token)
        list[0].type = DocBlockElementType.BLOCK_TEXT
        return list
        
    def _block_quote(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        block_list, raw_content, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type="block_quote",
            block_content=raw_content,
            children=id_list
        ))
        return block_list
        
    def _list_item(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        block_list, _, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type="list_item",
            children=id_list
        ))
        return block_list
        
    def _list(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        block_list, _, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type="list",
            children=id_list,
            block_attr={
                "depth": token["attrs"]["depth"],
                "ordered": token["attrs"]["ordered"],
                "bullet": token["bullet"]
            }
        ))
        return block_list
    
    def _table(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        return self._make_table_element(token, "table")
    
    def _table_head(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        return self._make_table_element(token, "table_head")
    
    def _table_body(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        return self._make_table_element(token, "table_body")

    def _table_row(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        return self._make_table_element(token, "table_row")
    
    def _table_cell(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        block_list, raw_content, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type="table_cell",
            block_content=raw_content,
            block_attr={
                "align": token["attrs"]["align"],
                "head": token["attrs"]["head"]
            },
            children=id_list
        ))
        return block_list
        
    def _make_table_element(self, token: Dict[str, Any], element_type: str) -> List[DocBlockElement]:
        block_list, _, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type=element_type,
            children=id_list,
        ))
        return block_list
    
    def _get_children_block_elements(self, token: Dict[str, Any]) -> Tuple[List[DocBlockElement], str, List[ObjectId]]:
        children = self._simplify_raw_text(token.get("children"))
        block_list = self.make_blocks(children)
        raw_content = self._parse_children_to_content(children)
        id_list = [block.id for block in block_list]
        return (block_list, raw_content, id_list)
    
    def _remove_elements_of_type(self, token_list: List[Dict[str, Any]], remove_types: List[Any]) -> List[Dict[str, Any]]: # move to type_parsing?
        removed_list: List[Dict[str, Any]] = []
        for item in token_list:
            if not item["type"] in remove_types:
                if item.get("children"):
                    item["children"] = self._remove_elements_of_type(item.get("children"), remove_types)
                removed_list.append(item)
        return removed_list

    def _parse_children_to_content(self, token_list: List[dict]) -> str: # move to type_parsing?
        '''
            Parses the content of embeded tokens in token_list from children dictionaries into one string. 
            Concatenates soft breaks and line breaks to the content string. 
            First searches for "raw" attribute in each dictionary representing a atomic element. 
            Secondly searches the "children" attribute and concatenates the content found in each element there. 
            Concatenates all content from children and raw to make a plaintext string representing the content found in 
            the element including all it's decendents. 
        '''
        content = ""
        to_add = ""
        for item in token_list:
            if item["type"] == "softbreak":
                content += " "
                continue
            elif item["type"] == "linebreak":
                content += "\n"
                continue

            if item.get("raw"):
                to_add = item["raw"]
            else:
                if item.get("children"):
                    to_add = self._parse_children_to_content(item["children"])
            
            content += to_add
        return content
    
    def _remove_bold_emphasis(self, token_list: List[Dict[str, Any]]): # move to type_parsing?
        for token in token_list:
            if token["type"] == "strong" or token["type"] == "emphasis": 
                token["raw"] = self._remove_bold_emphasis_helper([token]) 
                token["type"] = "text"
                token.pop("children")
        return token_list

    def _remove_bold_emphasis_helper(self, token_list: List[Dict[str, Any]]) -> str: # move to type_parsing?
        content = ""
        for token in token_list:
            raw = token.get("raw")
            child_list = token.get("children")
                                
            if raw:
                content += raw

            if child_list:
                content += self._remove_bold_emphasis_helper(child_list)
        
            if token["type"] == "strong":
                content = f"**{content}**"
            elif token["type"] == "emphasis":
                content = f"*{content}*"

        return content
    
    def _combine_text(self, token_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]: # move to type_parsing?
        if not token_list:
            return None

        new_token_list: List[Dict[str, Any]] = []
        
        content = ""
        for token in token_list:
            if token["type"] == "text" or token["type"] == "codespan":
                content += token["raw"]
            elif token["type"] == "linebreak":
                content += "\n"
            elif token["type"] == "softbreak":
                content += " "
            else:
                if content:
                    new_token_list.append({"type": "text", "raw": content})
                    content = ""
                new_token_list.append(token)
                
        if content:
            new_token_list.append({"type": "text", "raw": content})
        
        return new_token_list

    def _simplify_raw_text(self, token_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]: # move to type_parsing?
        return self._combine_text(self._remove_bold_emphasis(token_list))