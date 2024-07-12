import mistune
import os
import re

from mistune.plugins.table import table
from typing import List, Dict, Any, Optional, Tuple, Callable, Union
from bson import ObjectId
from builtins import Exception

from databasetools.models.block_model import DocBlockElement, DocBlockElementType

VALID_METADATA_VALUES = ["title", "id", "oneNoteId", "oneNotePath", "updated", "created"]

class Md2DocBlock:
    """Class for converting Markdown into DocBlockElements.

    Raises:
        AttributeError: _description_
        AttributeError: _description_
        Exception: _description_
        KeyError: _description_
        InvalidTokenError: _description_
        InvalidTokenError: _description_
        InvalidTokenError: _description_
        AttributeError: _description_
        NotRelativeURIWarning: _description_

    Returns:
        _type_: _description_
    """
    GENERIC_MODE = "generic"
    ONE_NOTE_MODE = "one_note"
    USER_DEFINED_MODE = "user_defined"
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
    
    def __init__(self, add_trim_tokens: Optional[List[str]] = None, mode_set: Optional[str] = GENERIC_MODE):
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
        self.func_list = self._default_func_list
        
        self._ignored_token_types = [self.TOKEN_TYPES["BLANK_LINE"]]
        if add_trim_tokens:
            self.add_ignored_types(add_trim_tokens)
        
        self.mode = mode_set
        
    @property
    def mode(self):
        return self._mode
    
    @mode.setter
    def mode(self, mode_to_set: str):
        if mode_to_set == self.GENERIC_MODE:
            self._mode = self.GENERIC_MODE
            self._func_list = self._default_func_list.copy()
        elif mode_to_set == self.ONE_NOTE_MODE:
            self._func_list = self._default_func_list.copy()
            self.override_func_list(DocBlockElementType.LINK, self._on_link)
            self.override_func_list(DocBlockElementType.IMAGE, self._on_image)
            self._mode = self.ONE_NOTE_MODE
        else:
            raise AttributeError(f"Invalid mode: {mode_to_set}")
        
    @property
    def func_list(self):
        """Shallow copy of parser list.

        Returns:
            Dict[TOKEN_TYPES, Callable]: A string-callable dictionary for each token type specified in Md2DocBlock.TOKEN_TYPES
        """
        return self._func_list.copy()
    
    @func_list.setter
    def func_list(self, set_func_list: Dict[DocBlockElementType, Callable]):
        self._func_list = set_func_list.copy()
    
    def override_func_list(self, token_parser_type: DocBlockElementType, token_parser_callable: Callable):
        """Sets the parse functions for each potential token type encountered in a markdown file. 

        Args:
            token_parser_type (Optional[DocBlockElementType]): Name of the token type to override or replace
            token_parser_callable (Optional[Callable]): Callable to replace the parser for a token type of token_parser_type.

        Raises:
            AttributeError: No parser type specified to override. 
        """
        if not token_parser_type and token_parser_callable:
            raise AttributeError(f"No token parser type given to override with {token_parser_callable}.")
        else:
            self._func_list[token_parser_type] = token_parser_callable
            self._mode = self.USER_DEFINED_MODE
    
    @property
    def ignored_token_types(self):
        return self._ignored_token_types.copy()
    
    @ignored_token_types.setter
    def ignored_token_types(self, token_types: List[str]):
        if not token_types:
            self._ignored_token_types = [self.TOKEN_TYPES["BLANK_LINE"]]
        else:
            self._ignored_token_types = token_types.copy()
            if not self.TOKEN_TYPES["BLANK_LINE"] in token_types:
                self._ignored_token_types.append(self.TOKEN_TYPES["BLANK_LINE"])
            
    def add_ignored_types(self, token_types: List[str]):
        for item in token_types:
            if not item in self._ignored_token_types and item:
                self._ignored_token_types.append(item)

    def remove_ignored_types(self, token_types: Union[List[str], str]):
        if isinstance(token_types, str):
            if token_types in self._ignored_token_types:
                self._ignored_token_types.remove(token_types)
        elif isinstance(token_types, list):
            for item in token_types:
                if item in self._ignored_token_types:
                    self._ignored_token_types.remove(item)

    # def process_page(self, file_path: Union[Path, str]) -> List[DocBlockElement]:
    #     file_path = Path(file_path)
        
    #     if file_path.suffix != ".md":
    #         raise NotMDFileError(f"File: {file_path} does not have a .md extension.") 
    #     elif not os.path.exists(file_path): 
    #         raise FileNotFoundError(f"The provided path: {file_path} does not exists.")
    #     elif not os.path.isfile(file_path):
    #         raise IsADirectoryError(f"The provided path: {file_path} is a directory. Use process_dir instead.")
        
    #     with open(file_path, "r") as f:
    #         metadata, md = frontmatter.parse(f.read())
            
    #     relative_path = os.path.relpath(file_path, self._home_dir_path)
        
    def md2docblock(self, md: str) -> Tuple[List[DocBlockElement], List[ObjectId]]:
        """Processes a string of Markdown and returns a list DocBlockElements along with a list of id's of the highest level DocBlockElements in the list.

        Args:
            md (str): Raw Markdown formatted string.

        Returns:
            Tuple[List[DocBlockElement], List[ObjectId]]: The first element is a list of DocBlockElements generated according to the raw markdown. The second list 
            is a list of ObjectId's of the highest level DocBlockElements from the Markdown string. 
        """
        token_list = self.md_to_token(md)
        id_list = []
        block_list = []
        for item in token_list:
            new_blocks = self.make_blocks([item])
            new_block_parent_id = new_blocks[0].id
            id_list.append(new_block_parent_id)
            block_list.extend(new_blocks)
        return block_list, id_list
        
    # def _process_generic_page(self, block_list: List[DocBlockElement], metadata: Dict[str, Any]) -> List[DocBlockElement]: #move?
    #     page_block = block_list[0]
    #     page_block.block_attr["frontmatter"] = metadata
    #     page_block.tags = [self.GENERIC_MODE]
    #     return block_list
        
    # def _process_oneNote_page(self, block_list: List[DocBlockElement], metadata: Dict[str, Any]) -> List[DocBlockElement]: # move?
    #     # OneNote export frontmatter has these fields
    #     # "metadata": {
    #     #     "title": "Platform Library",
    #     #     "id": "27bd2f39d4cc4017b64bc9b26645e0d5",
    #     #     "oneNoteId": "{DDD92369-7933-0FFD-3970-C986A571D816}{1}{E1838393364313073899420146992507433720312551}",
    #     #     "oneNotePath": null,
    #     #     "updated": "2021-01-25 18:16:06-08:00",
    #     #     "created": "2021-01-25 18:15:19-08:00"
    #     # }
        
    #     # oneNote_id_pattern = r"^{(.+)}{.}{(.+)}$"
    #     # on_id = metadata.get("oneNoteId")
    #     # match = re.match(oneNote_id_pattern, on_id)
    #     # section_id, other_id = match.groups()
    #     # page_id = str(uuid.UUID(hex=metadata.get("id"))).upper()
        
    #     page_block = block_list[0]
    #     page_block.name = str(metadata.get("title"))
    #     page_block.block_attr = {
    #         "oneNote_page_id": metadata.get("id"),
    #         "oneNoteId": metadata.get("oneNoteId"),
    #         # "oneNote_page_id": page_id,
    #         # "oneNote_section_id": section_id,
    #         # "oneNote_id": other_id,
    #         "oneNote_created_at": metadata.get("created"),
    #         "oneNote_modified_at": metadata.get("updated"),
    #         "oneNote_path": metadata.get("oneNotePath")
    #     }
    #     page_block.tags = [self.ONE_NOTE_MODE]
    #     return block_list
        
    def md_to_token(self, raw_md: str) -> List[Dict[str, Any]]:
        """Parses a raw Markdown string into python tokens.

        Args:
            raw_md (str): Raw string formatted in Markdown.

        Returns:
            List[Dict[str, Any]]: An Markdown AST generated by mistune.
        """
        bp = mistune.BlockParser(max_nested_level=10) # Instantiate a new block parser to a predefined max nesting level
        markdown = mistune.Markdown(renderer=None, block=bp, plugins=[table]) # renderer=None allows parsing to python tokens. Import other plugins as needed
        token_list = markdown(raw_md) 
        token_list = self._simplify_token_list(token_list)
        return self._remove_elements_of_type(token_list, self._ignored_token_types)
    
    def make_blocks(self, token_list: List[Dict[str, Any]]) -> List[DocBlockElement]:
        """Generates DocBlockElements from Markdown python tokens while maintaining block hierarchy with children list relation in each parent DocBlockElement.

        Args:
            token_list (List[Dict[str, Any]]): An Markdown AST from md_to_token.

        Raises:
            Exception: Re-raises exceptions from generating DocBlockElements with a description of the token make_blocks tried to parse.
            KeyError: When a Markdown token is passed in with an invalid type.

        Returns:
            List[DocBlockElement]: A list of DocBlockElements generated from token_list.
        """
        block_list = []
        for item in token_list:
            
            if not item:
                return None
        
            type = item["type"]
            if type in self._func_list:
                try:
                    new_block = self._func_list[type](item)
                except Exception as e:
                    raise Exception(f"Trying to add token: {item}") from e
            else:   
                raise KeyError(f"Invalid object type: {type} not in function list, in object: {item}")
            
            if isinstance(new_block, list):
                block_list.extend(new_block)
            else:
                block_list.append(new_block)
        block_list = [item for item in block_list if item is not None]
        return block_list
    
    # Atomic types
    def _text(self, token: Dict[str, Any]) -> DocBlockElement:
        """Generates a DocBlockElement for a token of type "text".

        Args:
            token (Dict[str, Any]): Should be a token with type: "text". 

        Returns:
            DocBlockElement: .type="text", .block_content="Raw text of the text token"
        """
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
        """Image parser for one

        Args:
            token (Dict[str, Any]): this is sick

        Returns:
            DocBlockElement: _description_
        """
        image_block = self._image(token)
        
        try:
            filename, extension = self._on_check_relative(token)
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
            filename, extension = self._on_check_relative(token)
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
        
    def _make_table_element(self, token: Dict[str, Any], element_type: DocBlockElementType) -> List[DocBlockElement]:
        block_list, _, id_list = self._get_children_block_elements(token)
        block_list.insert(0, DocBlockElement(
            type=element_type,
            children=id_list,
        ))
        return block_list
    
    def _block_html(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(
            type=DocBlockElementType.BLOCK_HTML,
            block_content=token["raw"]
        )
        
    def _strip_inline_HTML(self, token_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        new_token_list = []
        for token in token_list:
            if token["type"] == self.TOKEN_TYPES["INLINE_HTML"]:
                new_token = {
                    "type": self.TOKEN_TYPES["TEXT"],
                    "raw": token["raw"]
                }
                new_token_list.append(new_token)
            else:
                new_token_list.append(self.deep_copy_token(token))
        return new_token_list

    def _get_children_block_elements(self, token: Dict[str, Any]) -> Tuple[List[DocBlockElement], str, List[ObjectId]]:
        if not token:
            return ([], "", [])
        
        if not token.get("children"):
            return ([], "", [])
        
        children = self._simplify_token_list(token.get("children"))
        block_list = self.make_blocks(children)
        raw_content = self._token_list2str(children)
        id_list = [block.id for block in block_list]
        return (block_list, raw_content, id_list)
    
    def _remove_elements_of_type(self, token_list: List[Dict[str, Any]], remove_types: List[Any]) -> List[Dict[str, Any]]:
        cleaned_list: List[Dict[str, Any]] = []
        for token in token_list:
            if not token["type"]:
                continue # Don't append to new list
            
            if token["type"] in remove_types:
                continue # Don't append to new list
            
            # Do this if the type is valid
            new_token = token.copy()
            
            if token.get("children"):
                new_child_list = self._remove_elements_of_type(token.get("children"), remove_types)
                new_token["children"] = new_child_list
                
            if attrs := token.get("attrs"):
                new_attrs = self.deep_copy_token(attrs)
                token["attrs"] = new_attrs

            cleaned_list.append(new_token)
                
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
        for item in token_list:
            if item["type"] == self.TOKEN_TYPES["SOFTBREAK"]:
                content += " "
            elif item["type"] == self.TOKEN_TYPES["LINEBREAK"]:
                content += "\n"
            elif item.get("raw"):
                content += item["raw"]
            elif item.get("children"):
                content += self._token_list2str(item["children"])
        return content
    
    def _simplify_token_list(self, token_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]: 
        '''
            Removes strong and emphasis tokens.
            Concatenates consecutive text, linebreaks, and softbreak tokens. 
        '''
        if not token_list:
            return None
        
        new_token_list: List[Dict[str, Any]] = []
        
        for token in token_list:
            if token["type"] == self.TOKEN_TYPES["STRONG"] or token["type"] == self.TOKEN_TYPES["EMPHASIS"]: 
                new_token = {
                    "type": self.TOKEN_TYPES["TEXT"],
                    "raw": self._extract_bold_emphasis_content([token])
                }
                new_token_list.append(new_token)
            else:
                new_token_list.append(self.deep_copy_token(token))
                
        new_token_list = self._strip_inline_HTML(new_token_list)
        
        final_list: List[Dict[str, Any]] = []
        content = ""
        for token in new_token_list:
            if token["type"] == self.TOKEN_TYPES["TEXT"]:
                content += token["raw"]
            elif token["type"] == self.TOKEN_TYPES["CODESPAN"]:
                content += f"""`{token["raw"]}`"""
            elif token["type"] == self.TOKEN_TYPES["LINEBREAK"]:
                content += "\n"
            elif token["type"] == self.TOKEN_TYPES["SOFTBREAK"]:
                content += " "
            else:
                if content:
                    final_list.append({"type": self.TOKEN_TYPES["TEXT"], "raw": content})
                    content = ""
                final_list.append(self.deep_copy_token(token))
                
        if content:
            final_list.append({"type": self.TOKEN_TYPES["TEXT"], "raw": content})
        return final_list
    
    def _extract_bold_emphasis_content(self, token_list: List[Dict[str, Any]]) -> str: 
        '''
            This is a helper function and should only be called by _simplify_token_list
        '''
        content = ""
        allowed_types = [self.TOKEN_TYPES["STRONG"], self.TOKEN_TYPES["EMPHASIS"], self.TOKEN_TYPES["TEXT"]]
        for token in token_list:
            if not token["type"] in allowed_types:
                raise InvalidTokenError(f"Token: {token} cannot be simplified with {self._extract_bold_emphasis_content}")
            
            raw = token.get("raw")
            child_list = token.get("children")
                                
            if raw:
                content += raw

            if child_list:
                content += self._extract_bold_emphasis_content(child_list)
        
            if token["type"] == self.TOKEN_TYPES["STRONG"]:
                content = f"**{content}**"
            elif token["type"] == self.TOKEN_TYPES["EMPHASIS"]:
                content = f"*{content}*"

        return content
    
    def _on_check_relative(self, token: Dict[str, Any]):
        raw_uri = token.get("attrs").get("url")
        
        if not raw_uri:
            raise AttributeError(f"No url field in this token: {token}.")
        
        path_pattern = r"^(?:\.\.\/)*resources\/(.*)$"
        match = re.match(path_pattern, raw_uri)
        if match:
            return os.path.splitext(match.group(1))
        else:
            raise NotRelativeURIWarning(f"Provided token does not contain a relative URI for a oneNote Export: {token}")
    
    def deep_copy_token(self, token: Dict[str, Any]) -> Dict[str, Any]:
        new_token = token.copy()
        for attr in new_token:
            if isinstance(token[attr], list):
                new_token[attr] = self.deep_copy_token_list(token[attr])
            elif isinstance(token[attr], dict):
                new_token[attr] = self.deep_copy_token(token[attr])
        return new_token
        
    def deep_copy_token_list(self, token_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        new_list = token_list.copy()
        for item in new_list:
            if isinstance(item, list):
                item = self.deep_copy_token_list(item)
            elif isinstance(item, dict):
                item = self.deep_copy_token(item)
        return new_list

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