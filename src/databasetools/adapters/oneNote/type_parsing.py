import mistune
import os
import frontmatter
import re

from mistune.plugins.table import table
from typing import List, Dict, Any, Union, Tuple, Callable
from bson import ObjectId
from pathlib import Path
from builtins import Exception
from databasetools.models.block_model import DocBlockElement, DocBlockElementType

VALID_METADATA_VALUES = ["title", "id", "oneNoteId", "oneNotePath", "updated", "created"]

class Md2DocBlock:
    GENERIC_MODE = "generic"
    ONE_NOTE_MODE = "one_note"
    
    TOKEN_TYPES = {
        # Raw string representation of each token type key given by mistune
        "TEXT": "text",
        "HEADING": "heading",
        "BLOCK_CODE": "block_code",
        "CODESPAN": "codespan",
        
        "PARAGRAPH": "paragraph",
        "BLOCK_TEXT": "block_text",
        "LINK": "link",
        "IMAGE": "image",
        "BLOCK_QUOTE": "block_quote",
        "LIST_ITEM": "list_item",
        "LIST": "list",
        
        "TABLE": "table",
        "TABLE_HEAD": "table_head",
        "TABLE_BODY": "table_body",
        "TABLE_ROW": "table_row",
        "TABLE_CELL": "table_cell",
        
        "THEMATIC_BREAK": "thematic_break",
        
        "BLOCK_HTML": "block_html",
        "INLINE_HTML": "inline_html",
        
        "SOFTBREAK": "softbreak",
        "LINEBREAK": "linebreak",
        "STRONG": "strong",
        "EMPHASIS": "emphasis",
        "BLANK_LINE": "blank_line",
    }
    
    def __init__(self, export_mode: str = GENERIC_MODE):
        self.export_mode = export_mode
        self.set_parser() # Sets token parsing function list
        self.set_export_mode(self.export_mode)
        
    def reset(self):
        self.__init__()
        
    def set_export_mode(self, export_mode: str = GENERIC_MODE):
        self.export_mode = export_mode
        if export_mode == self.GENERIC_MODE: # Default behavior
            self.set_parser()
        elif export_mode == self.ONE_NOTE_MODE: # Overrides image and link parsers to accommodate relative references.
            self.set_parser(DocBlockElementType.LINK, self._on_link)
            self.set_parser(DocBlockElementType.IMAGE, self._on_image)
        else:
            raise InvalidExportMode(f"Cannot set export mode to {export_mode}.")
            
    def set_parser(self, token_parser_type: DocBlockElementType = None, token_parser_callable: Callable = None):
        if not token_parser_type and not token_parser_callable:
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
                DocBlockElementType.TABLE_CELL: self._table_cell,
                
                # HTML types
                DocBlockElementType.BLOCK_HTML: self._block_html
            }
        elif not token_parser_type:
            raise AttributeError("No token parser type given to override.")
        else:
            self.func_list[token_parser_type] = token_parser_callable
            
    def process_page(self, file_path: Union[Path, str]) -> List[DocBlockElement]:
        file_path = Path(file_path)
        
        if file_path.suffix != ".md":
            raise NotMDFileError(f"File: {file_path} does not have a .md extension.") 
        elif not os.path.exists(file_path): 
            raise FileNotFoundError(f"The provided path: {file_path} does not exists.")
        elif not os.path.isfile(file_path):
            raise IsADirectoryError(f"The provided path: {file_path} is a directory. Use process_dir instead.")
        
        with open(file_path, "r") as f:
            metadata, md = frontmatter.parse(f.read())
        
        # Markdown Extraction and conversion to DocBlockElements
        token_list = self.md_to_token(md)
        page_block_list = self.make_blocks(token_list)
        id_list = [block.id for block in page_block_list]
        page_block_list.insert(0, DocBlockElement(
            type=DocBlockElementType.PAGE,
            children=id_list
        ))
        
        if self.export_mode == self.GENERIC_MODE:
            page_block_list = self._process_generic_page(page_block_list, metadata)
        elif self.export_mode == self.ONE_NOTE_MODE:
            page_block_list = self._process_oneNote_page(page_block_list, metadata)
        else:
            raise AttributeError(f"Invalid attribute: {self.export_mode}, when trying to blockify: {file_path}")
        
        page_block = page_block_list[0]
        page_block.block_attr["local_path"] = str(file_path)
        page_block.block_attr["file_name"] = os.path.splitext(os.path.basename(file_path))[0]
        
        return page_block_list
        
    def _process_generic_page(self, block_list: List[DocBlockElement], metadata: Dict[str, Any]) -> List[DocBlockElement]:
        page_block = block_list[0]
        page_block.block_attr["frontmatter"] = metadata
        page_block.tags = [self.GENERIC_MODE]
        return block_list
        
    def _process_oneNote_page(self, block_list: List[DocBlockElement], metadata: Dict[str, Any]) -> List[DocBlockElement]: 
        # OneNote export frontmatter has these fields
        # "metadata": {
        #     "title": "Platform Library",
        #     "id": "27bd2f39d4cc4017b64bc9b26645e0d5",
        #     "oneNoteId": "{DDD92369-7933-0FFD-3970-C986A571D816}{1}{E1838393364313073899420146992507433720312551}",
        #     "oneNotePath": null,
        #     "updated": "2021-01-25 18:16:06-08:00",
        #     "created": "2021-01-25 18:15:19-08:00"
        # }
        
        # Metadata updates
        page_block = block_list[0]
        page_block.name = str(metadata.get("title"))
        page_block.block_attr = {
            "oneNote_pageid": metadata.get("id"),
            "oneNoteId": metadata.get("oneNoteId"),
            "oneNote_created_at": metadata.get("created"),
            "oneNote_modified_at": metadata.get("updated"),
            "oneNote_path": metadata.get("oneNotePath")
        }
        page_block.tags = [self.ONE_NOTE_MODE]
        return block_list
        
    def md_to_token(self, raw_md: str) -> List[Dict[str, Any]]:
        '''
            Parses markdown into python tokens using mistune.
        '''
        remove_types = [self.TOKEN_TYPES["BLANK_LINE"], None] # Add elements here if you need to trim the parsing
        bp = mistune.BlockParser(max_nested_level=10) # Instantiate a new block parser to a predefined max nesting level
        markdown = mistune.Markdown(renderer=None, block=bp, plugins=[table]) # renderer=None allows parsing to python tokens. Import other plugins as needed
        token_list = markdown(raw_md) 
        token_list = self._simplify_token_list(token_list)
        return self._remove_elements_of_type(token_list, remove_types)
        
    def make_block(self, token: Dict[str, Any]):
        '''
            Checks the type of the input then calls the corresponding function from the function list.
            May return one DocBlockElement or a list of DocBlockElements 
        '''
        if not token:
            return None
        
        type = token["type"]
        if type in self.func_list:
            try:
                return self.func_list[type](token)
            except Exception as e:
                raise Exception(f"Trying to add token: {token}") from e
        else:   
            raise KeyError(f"Invalid object type: {type} not in function list, in object: {token}")
    
    def make_blocks(self, token_list: List[Dict[str, Any]]) -> List[DocBlockElement]:
        '''
            Repeatedly calls the make_block method to make a list of DocBlockElements from a list of tokens. 
        '''
        block_list = []
        for item in token_list:
            new_block = self.make_block(item)
            if isinstance(new_block, list):
                block_list.extend(new_block)
            else:
                block_list.append(new_block)
        block_list = [item for item in block_list if item is not None]
        return block_list
    
    # Atomic types
    def _text(self, token: Dict[str, Any]) -> DocBlockElement:
        '''
            type: "text"
            block_content: Attempts to get the raw content of the token. 
        '''
        
        raw_content = token.get("raw")
        if not raw_content: # Don't make text docblocks that are empty
            return None
        
        return DocBlockElement(
            type=DocBlockElementType.TEXT,
            block_content=raw_content
        )

    def _heading(self, token: Dict[str, Any]) -> DocBlockElement:
        '''
            type: "heading"
            block_attr: Stores the heading level under "level" which is located at token->attrs->level
            block_content: Stripped raw text
        '''
        raw_content = self._simplify_token_list(token["children"])
        
        if len(raw_content) > 1:
            raise InvalidTokenError(f"Attempting to parse invalid heading token with unsupported markdown syntax: {token}")
        elif len(raw_content) == 0:
            return None
        
        return DocBlockElement(
            type=DocBlockElementType.HEADING,
            block_attr={"level": token["attrs"]["level"]},
            block_content=raw_content[0]["raw"]
        )
    
    def _block_code(self, token: Dict[str, Any]) -> DocBlockElement:
        '''
            type: "block_code"
            block_attr: Stores the language if any under "language"
            block_content: Stores the raw content of the code block
        '''
        if token_attrs := token.get("attrs"):
            language = token_attrs.get("info")
        else:
            language = None
        return DocBlockElement(
            type=DocBlockElementType.BLOCK_CODE,
            block_attr={"language": language},
            block_content=token["raw"]
        )
        
    def _codespan(self, token: Dict[str, Any]) -> DocBlockElement:
        '''
            type: "codespan"
            block_content: Stores raw content
        '''
        
        raw_content = token.get("raw")
        if not raw_content:
            return None
        
        return DocBlockElement(
            type=DocBlockElementType.CODESPAN,
            block_content=raw_content
        )
        
    def _thematic_break(self, _) -> DocBlockElement:
        '''
            type: "thematic_break"
        '''
        return DocBlockElement(
            type=DocBlockElementType.THEMATIC_BREAK
        )
        
    # Derived types
    def _image(self, token: Dict[str, Any]) -> DocBlockElement:
        '''
            type: "image"
            block_content: Contains all the raw alt text for the image.
            block_attr["url"]: Contains the url for the image.
        '''
        raw_text = self._simplify_token_list(token.get("children"))
        if len(raw_text) > 1:
            raise InvalidTokenError(f"Image token: {token} contains unexpected markdown syntax.")
        
        return DocBlockElement(
            type=DocBlockElementType.IMAGE,
            block_content=self._token_list2str(raw_text),
            block_attr={
                "url": token["attrs"]["url"]
            }
        )
        
    def _on_image(self, token: Dict[str, Any]) -> DocBlockElement:
        image_block = self._image(token)
        
        try:
            filename, extension = self._check_relative(token)
        except NotRelativeURIWarning: # No relative link found
            return image_block
        
        image_block.type = DocBlockElementType.RESOURCE_REFERENCE
        image_block.status = "Unverified"
        image_block.block_attr = {
            "filename": filename,
            "extension": extension
        }
        return image_block
    
    def _link(self, token: Dict[str, Any]) -> List[DocBlockElement]: 
        '''
            For parsing normal markdown links
            type: "link"
            block_content: Contains all raw text of the link.
            block_attr["url"]: Contains the urls of the link.
            children: Contains id's of text and image blocks that may be contained in the link. 
        '''
        block_list, raw_content, id_list = self._get_children_block_elements(token)
        
        block_list.insert(0, DocBlockElement(
            type=DocBlockElementType.LINK,
            block_content=raw_content,
            block_attr={"url": token["attrs"]["url"]},
            children=id_list
        ))
        
        return block_list
    
    def _on_link(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        '''
            For parsing markdown links that may contain references to a resource folder like the one in exports from the One Note Export Tool.
            Should only be used if parsing One Note Exports using https://github.northgrum.com/cosgrma/onenote-exporter.git
        '''
        link_blocks = self._link(token)
        
        try:
            filename, extension = self._check_relative(token)
        except NotRelativeURIWarning: # No relative link found
            return link_blocks
        
        link_block = link_blocks[0]
        link_block.type = DocBlockElementType.RESOURCE_REFERENCE
        link_block.block_attr = {
            "filename": filename,
            "extension": extension
        }
        link_block.status = "Unverified"
        return link_blocks
        
    def _paragraph(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        '''
            type: "paragraph"
            block_content: All raw text of the paragraph block. 
            children: Id's of children blocks.
        '''
        block_list, raw_content, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type=DocBlockElementType.PARAGRAPH,
            block_content=raw_content,
            children=id_list
        ))
        return block_list
    
    def _block_text(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        '''
            Paragraph with different type name
        '''
        list = self._paragraph(token)
        list[0].type = DocBlockElementType.BLOCK_TEXT
        return list
        
    def _block_quote(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        '''
            type: "block_quote"
            block_content: Should be all the raw content of the block and its children.
            children: List of id's of the children DocBlockElements that this block inherits. 
        '''
        block_list, raw_content, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type=DocBlockElementType.BLOCK_QUOTE,
            block_content=raw_content,
            children=id_list
        ))
        return block_list
        
    def _list_item(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        '''
            type: "list_item"
            children: id list containing children (types?)
        '''
        block_list, _, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type=DocBlockElementType.LIST_ITEM,
            children=id_list
        ))
        return block_list
        
    def _list(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        '''
            type: "list"
            children: Should only contain id's for DocBlockElements of type "list" or "list_item"
            block_attr: 
                depth: Stores the depth of the list if there is nesting
                ordered: True or False if the list is ordered
                bullet: If the list was shot out of a gun. (point style actually)
        '''
        block_list, _, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type=DocBlockElementType.LIST,
            children=id_list,
            block_attr={
                "depth": token["attrs"]["depth"],
                "ordered": token["attrs"]["ordered"],
                "bullet": token["bullet"]
            }
        ))
        return block_list
    
    # Table Blocks
    def _table(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        return self._make_table_element(token, DocBlockElementType.TABLE)
    
    def _table_head(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        return self._make_table_element(token, DocBlockElementType.TABLE_HEAD)
    
    def _table_body(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        return self._make_table_element(token, DocBlockElementType.TABLE_BODY)

    def _table_row(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        return self._make_table_element(token, DocBlockElementType.TABLE_ROW)
    
    def _table_cell(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        block_list, raw_content, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type=DocBlockElementType.TABLE_CELL,
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
    
    def _block_html(self, token: Dict[str, Any]) -> List[DocBlockElement]:
        return DocBlockElement(
            type=DocBlockElementType.BLOCK_HTML,
            block_content=token["raw"]
        )
        
    def _strip_inline_HTML(self, token_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        new_token_list = []
        for token in token_list:
            if token["type"] != self.TOKEN_TYPES["INLINE_HTML"]:
                new_token_list.append(token)
        return new_token_list

    def _get_children_block_elements(self, token: Dict[str, Any]) -> Tuple[List[DocBlockElement], str, List[ObjectId]]:
        if not token.get("children"):
            return ([], "", [])
        
        children = self._simplify_token_list(token.get("children"))
        block_list = self.make_blocks(children)
        raw_content = self._token_list2str(children)
        id_list = [block.id for block in block_list]
        return (block_list, raw_content, id_list)
    
    def _remove_elements_of_type(self, token_list: List[Dict[str, Any]], remove_types: List[Any]) -> List[Dict[str, Any]]:
        cleaned_list: List[Dict[str, Any]] = []
        for item in token_list:
            if not item["type"] in remove_types:
                if item.get("children"):
                    item["children"] = self._remove_elements_of_type(item.get("children"), remove_types)
                cleaned_list.append(item)
        return cleaned_list

    def _token_list2str(self, token_list: List[dict]) -> str:
        '''
            Parses the content of embedded tokens in token_list from children dictionaries into one string. 
            Concatenates soft breaks and line breaks to the content string. 
            First searches for "raw" attribute in each dictionary representing a atomic element. 
            Secondly searches the "children" attribute and concatenates the content found in each element there. 
            Concatenates all content from children and raw to make a plaintext string representing the content found in 
            the element including all it's descendants. 
        '''
        content = ""
        to_add = ""
        for item in token_list:
            if item["type"] == self.TOKEN_TYPES["SOFTBREAK"]:
                content += " "
                continue
            elif item["type"] == self.TOKEN_TYPES["LINEBREAK"]:
                content += "\n"
                continue

            if item.get("raw"):
                to_add = item["raw"]
            else:
                if item.get("children"):
                    to_add = self._token_list2str(item["children"])
            
            content += to_add
        return content
    
    def _simplify_token_list(self, token_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]: 
        '''
            Removes strong and emphasis tokens.
            Concatenates consecutive text, linebreaks, and softbreak tokens. 
        '''
        if not token_list:
            return None
        
        for token in token_list:
            if token["type"] == self.TOKEN_TYPES["STRONG"] or token["type"] == self.TOKEN_TYPES["EMPHASIS"]: 
                token["raw"] = self._remove_bold_emphasis([token]) 
                token["type"] = self.TOKEN_TYPES["TEXT"]
                token.pop("children")
        
        token_list = self._strip_inline_HTML(token_list)

        new_token_list: List[Dict[str, Any]] = []
        
        content = ""
        for token in token_list:
            if token["type"] == self.TOKEN_TYPES["TEXT"] or token["type"] == self.TOKEN_TYPES["CODESPAN"]:
                content += token["raw"]
            elif token["type"] == self.TOKEN_TYPES["LINEBREAK"]:
                content += "\n"
            elif token["type"] == self.TOKEN_TYPES["SOFTBREAK"]:
                content += " "
            else:
                if content:
                    new_token_list.append({"type": self.TOKEN_TYPES["TEXT"], "raw": content})
                    content = ""
                new_token_list.append(token)
                
        if content:
            new_token_list.append({"type": self.TOKEN_TYPES["TEXT"], "raw": content})
        return new_token_list
    
    def _remove_bold_emphasis(self, token_list: List[Dict[str, Any]]) -> str: 
        content = ""
        for token in token_list:
            raw = token.get("raw")
            child_list = token.get("children")
                                
            if raw:
                content += raw

            if child_list:
                content += self._remove_bold_emphasis(child_list)
        
            if token["type"] == self.TOKEN_TYPES["STRONG"]:
                content = f"**{content}**"
            elif token["type"] == self.TOKEN_TYPES["EMPHASIS"]:
                content = f"*{content}*"

        return content
    
    def _check_relative(self, token: Dict[str, Any]):
        raw_uri = token.get("attrs").get("url")
        
        if not raw_uri:
            raise AttributeError(f"No url field in this token: {token}.")
        
        path_pattern = r"^(?:\.\.\/)*resources\/(.*\..*)$"
        match = re.findall(path_pattern, raw_uri)
        if len(match) == 1:
            return os.path.splitext(match[0])
        elif len(match) == 0: 
            raise NotRelativeURIWarning(f"Provided token does not contain a relative URI: {token}")
        else:
            raise InvalidTokenError(f"Relative URI Regex found multiple matches in: {token}")
        
class InvalidTokenError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class NotMDFileError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class InvalidExportMode(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        
class NotRelativeURIWarning(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)