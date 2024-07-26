import re
from builtins import Exception
from pathlib import Path
from pprint import pprint
from textwrap import indent
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import mistune
import mistune.renderers
import mistune.renderers.markdown
from bson import ObjectId
from mistune.core import BaseRenderer
from mistune.core import BlockState
from mistune.plugins.table import table
from mistune.renderers.markdown import MarkdownRenderer

from databasetools.models.docblock import DocBlockElement
from databasetools.models.docblock import DocBlockElementType

DEBUG = False


def debug_print(item):
    if DEBUG:
        pprint(item, sort_dicts=False)


class MdRenderer(MarkdownRenderer):
    def table(self, token: Dict[str, Any], state: BlockState):
        out = ""
        for child in token["children"]:
            out += self.render_token(child, state) + "\n"
        return out

    def table_head(self, token: Dict[str, Any], state: BlockState):
        header_1 = ""
        header_2 = ""

        for child in token["children"]:
            header_1 += "| " + self.render_token(child, state) + " "
            attrs = child.get("attrs")
            alignment = attrs.get("align") if attrs else None

            if alignment == "left":
                header_2 += "| :--- "
            elif alignment == "right":
                header_2 += "| ---: "
            elif alignment == "center":
                header_2 += "| :---: "
            elif not alignment:
                header_2 += "| --- "

        header_2 += "|"
        header_1 += "|"
        return header_1 + "\n" + header_2

    def table_body(self, token: Dict[str, Any], state: BlockState):
        out = ""
        for child in token["children"]:
            out += self.render_token(child, state) + "\n"
        return out

    def table_row(self, token: Dict[str, Any], state: BlockState):
        out = ""
        for child in token["children"]:
            out += "| " + self.render_token(child, state) + " "
        out += "|"
        return out

    def table_cell(self, token: Dict[str, Any], state: BlockState):
        return self.render_children(token, state)

    def block_quote(self, token: Dict[str, Any], state: BlockState) -> str:
        text = self.render_children(token, state)
        if len(token["children"]) == 1 and token["children"][0]["type"] == "block_quote":
            text = text.rstrip()

        return indent(text, "> ", lambda _: True) + "\n\n"


class FromDocBlock:
    def __init__(self, block_list: List[DocBlockElement], resource_prefix: Optional[Union[Path, str]] = None):
        self._default_func_list = {
            DocBlockElementType.TEXT: self._text,
            DocBlockElementType.EMPHASIS: self._emphasis,
            DocBlockElementType.STRONG: self._strong,
            DocBlockElementType.LINK: self._link,
            DocBlockElementType.IMAGE: self._image,
            DocBlockElementType.CODESPAN: self._codespan,
            DocBlockElementType.LINE_BREAK: self._line_break,
            DocBlockElementType.SOFT_BREAK: self._soft_break,
            DocBlockElementType.BLANK_LINE: self._blank_line,
            DocBlockElementType.INLINE_HTML: self._inline_html,
            DocBlockElementType.PARAGRAPH: self._paragraph,
            DocBlockElementType.HEADING: self._heading,
            DocBlockElementType.THEMATIC_BREAK: self._thematic_break,
            DocBlockElementType.BLOCK_TEXT: self._block_text,
            DocBlockElementType.BLOCK_CODE: self._block_code,
            DocBlockElementType.BLOCK_QUOTE: self._block_quote,
            DocBlockElementType.BLOCK_HTML: self._block_html,
            DocBlockElementType.LIST_ITEM: self._list_item,
            DocBlockElementType.LIST: self._list,
            DocBlockElementType.TABLE: self._table,
            DocBlockElementType.TABLE_HEAD: self._table_head,
            DocBlockElementType.TABLE_BODY: self._table_body,
            DocBlockElementType.TABLE_ROW: self._table_row,
            DocBlockElementType.TABLE_CELL: self._table_cell,
            DocBlockElementType.RESOURCE_REFERENCE: self._resource_reference,
        }
        self._resource_prefix = Path(resource_prefix) if resource_prefix else None
        self._required_resources: List[str] = []
        self.func_list = self._default_func_list.copy()
        self.__block_cache: Dict[ObjectId, DocBlockElement] = {block.id: block for block in block_list}

    @classmethod
    def render_docBlock(
        cls,
        block_list: List[DocBlockElement],
        id_list: List[ObjectId],
        renderer: Optional[BaseRenderer] = None,
        resource_prefix: Optional[Union[Path, str]] = None,
    ) -> Tuple[str, List[str]]:
        """Renders a list of DocBlockElement's into a formatted string.

        Args:
            block_list (List[DocBlockElement]): A list of DocBlockElement's that consist of all elements in a document tree/forest.
            id_list (List[ObjectId]): A list of root nodes for constructing the elements of the tree.
            renderer (BaseRenderer, optional): A mistune renderer to render to different formats. Defaults to MdRenderer.
            resource_prefix (Union[Path, str], optional): Prefix used before the basename of relative resource references in the URL field. Defaults to None.

        Returns:
            Tuple[str, List[str]]: Output Markdown string, list of resources needed to render page.
        """
        if renderer is None:
            renderer = MdRenderer()

        parser = cls(block_list, resource_prefix)
        token_list = []
        for id in id_list:
            block = parser.get_block(id)
            token = parser.make_token(block)
            token_list.append(token)

        debug_print(token_list)

        block_state = BlockState()
        for token in token_list:
            block_state.append_token(token)

        md_render = mistune.Markdown(renderer=renderer, plugins=[table])
        return (md_render.render_state(block_state), parser._required_resources.copy())

    def make_token(self, block: DocBlockElement) -> Dict[str, Any]:
        b_type = block.type

        if b_type in self.func_list:
            try:
                new_token = self.func_list[b_type](block)
            except Exception as e:
                raise Exception(f"While parsing block: {block}") from e
        else:
            raise KeyError(f"invalid block: {block}")

        return new_token

    def make_children_token(self, block: DocBlockElement) -> List[Dict[str, Any]]:
        id_list = block.children
        child_list = []
        for id in id_list:
            block = self.get_block(id)
            token = self.make_token(block)
            child_list.append(token)
        return child_list

    def get_block(self, id: ObjectId) -> DocBlockElement:
        block = self.__block_cache.get(id)
        if block:
            self.__block_cache.pop(id)
            return block
        else:
            raise MissingBlockElements(id)

    def _text(self, block: DocBlockElement) -> Dict[str, Any]:
        return {"type": DocBlockElementType.TEXT.value, "raw": block.block_content}

    def _emphasis(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        return {"type": DocBlockElementType.EMPHASIS.value, "children": child_list}

    def _strong(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        return {"type": DocBlockElementType.STRONG.value, "children": child_list}

    def _link(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        b_attr = block.block_attr
        attr = {"url": b_attr.get("url"), "title": b_attr.get("title")}
        return {"type": DocBlockElementType.LINK.value, "children": child_list, "attrs": attr}

    def _image(self, block: DocBlockElement) -> Dict[str, Any]:
        token = self.func_list[DocBlockElementType.LINK](block)
        token["type"] = DocBlockElementType.IMAGE.value
        return token

    def _codespan(self, block: DocBlockElement) -> Dict[str, Any]:
        return {"type": DocBlockElementType.CODESPAN.value, "raw": block.block_content}

    def _line_break(self, block: DocBlockElement) -> Dict[str, Any]:
        return {"type": DocBlockElementType.LINE_BREAK.value}

    def _soft_break(self, block: DocBlockElement) -> Dict[str, Any]:
        return {"type": DocBlockElementType.SOFT_BREAK.value}

    def _blank_line(self, block: DocBlockElement) -> Dict[str, Any]:
        return {"type": DocBlockElementType.BLANK_LINE.value}

    def _inline_html(self, block: DocBlockElement) -> Dict[str, Any]:
        return {"type": DocBlockElementType.INLINE_HTML.value, "raw": block.block_content}

    def _paragraph(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        return {"type": DocBlockElementType.PARAGRAPH.value, "children": child_list}

    def _heading(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        level = block.block_attr.get("level")
        return {"type": DocBlockElementType.HEADING.value, "attrs": {"level": level}, "children": child_list}

    def _thematic_break(self, block: DocBlockElement) -> Dict[str, Any]:
        return {"type": DocBlockElementType.THEMATIC_BREAK.value}

    def _block_text(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        return {"type": DocBlockElementType.BLOCK_TEXT.value, "children": child_list}

    def _block_code(self, block: DocBlockElement) -> Dict[str, Any]:
        attrs = {"info": block.block_attr.get("language")} if block.block_attr.get("language") else None
        return {"type": DocBlockElementType.BLOCK_CODE.value, "attrs": attrs, "raw": block.block_content}

    def _block_quote(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        return {"type": DocBlockElementType.BLOCK_QUOTE.value, "children": child_list}

    def _block_html(self, block: DocBlockElement) -> Dict[str, Any]:
        return {"type": DocBlockElementType.BLOCK_HTML.value, "raw": block.block_content}

    def _list(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        attrs = {"ordered": True if block.block_attr["ordered"] else False, "depth": block.block_attr.get("depth")}
        return {
            "type": DocBlockElementType.LIST.value,
            "children": child_list,
            "attrs": attrs,
            "bullet": block.block_attr.get("bullet"),
            "tight": block.block_attr.get("tight"),
        }

    def _list_item(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        return {"type": DocBlockElementType.LIST_ITEM.value, "children": child_list}

    def _table(self, block: DocBlockElement) -> Dict[str, Any]:
        return self.make_table_token(block, DocBlockElementType.TABLE)

    def _table_head(self, block: DocBlockElement) -> Dict[str, Any]:
        return self.make_table_token(block, DocBlockElementType.TABLE_HEAD)

    def _table_body(self, block: DocBlockElement) -> Dict[str, Any]:
        return self.make_table_token(block, DocBlockElementType.TABLE_BODY)

    def _table_row(self, block: DocBlockElement) -> Dict[str, Any]:
        return self.make_table_token(block, DocBlockElementType.TABLE_ROW)

    def _table_cell(self, block: DocBlockElement) -> Dict[str, Any]:
        child_list = self.make_children_token(block)
        attrs = {"align": block.block_attr.get("align"), "head": block.block_attr.get("head")}
        return {"type": DocBlockElementType.TABLE_CELL.value, "children": child_list, "attrs": attrs}

    def _resource_reference(self, block: DocBlockElement) -> Dict[str, Any]:
        attrs = block.block_attr
        orig_type = attrs.get("type") if attrs else None
        basename = attrs.get("basename") if attrs else None
        if orig_type == DocBlockElementType.IMAGE.value:
            token = self._image(block)
        elif orig_type == DocBlockElementType.LINK.value:
            token = self._link(block)

        new_token_attrs = token.get("attrs")
        new_token_attrs["url"] = str(self._resource_prefix / basename) if self._resource_prefix else basename
        self._required_resources.append(basename)
        return token

    def make_table_token(self, block: DocBlockElement, element: DocBlockElementType):
        child_list = self.make_children_token(block)
        return {"type": element.value, "children": child_list}


class ToDocBlock:
    GENERIC_MODE = "generic"
    ONE_NOTE_MODE = "one_note"
    USER_DEFINED_MODE = "user_defined"

    def __init__(self, mode_set: Optional[str] = GENERIC_MODE):
        """Initializes an Md2DocBlock instance.

        Args:
            ignore_token_type_list (Optional[List[str]], optional): additional list of token types for the parser to ignore. Parser automatically ignores None types and "blank_line" types. Defaults to None.
            mode_set (Optional[str], optional): Parsing mode. Can be "Generic", "oneNote", or "User_Defined". Defaults to GENERIC_MODE.
        """
        self._default_func_list = {
            DocBlockElementType.TEXT: self._text,
            DocBlockElementType.EMPHASIS: self._emphasis,
            DocBlockElementType.STRONG: self._strong,
            DocBlockElementType.LINK: self._link,
            DocBlockElementType.IMAGE: self._image,
            DocBlockElementType.CODESPAN: self._codespan,
            DocBlockElementType.LINE_BREAK: self._line_break,
            DocBlockElementType.SOFT_BREAK: self._soft_break,
            DocBlockElementType.BLANK_LINE: self._blank_line,
            DocBlockElementType.INLINE_HTML: self._inline_html,
            DocBlockElementType.PARAGRAPH: self._paragraph,
            DocBlockElementType.HEADING: self._heading,
            DocBlockElementType.THEMATIC_BREAK: self._thematic_break,
            DocBlockElementType.BLOCK_TEXT: self._block_text,
            DocBlockElementType.BLOCK_CODE: self._block_code,
            DocBlockElementType.BLOCK_QUOTE: self._block_quote,
            DocBlockElementType.BLOCK_HTML: self._block_html,
            DocBlockElementType.LIST_ITEM: self._list_item,
            DocBlockElementType.LIST: self._list,
            DocBlockElementType.TABLE: self._table,
            DocBlockElementType.TABLE_HEAD: self._table_head,
            DocBlockElementType.TABLE_BODY: self._table_body,
            DocBlockElementType.TABLE_ROW: self._table_row,
            DocBlockElementType.TABLE_CELL: self._table_cell,
        }
        self.func_list = self._default_func_list

        self.mode = mode_set

        self.__block_list: List[DocBlockElement] = []

    @classmethod
    def parse_md2docblock(cls, md: str, mode: Optional[str] = GENERIC_MODE) -> Tuple[List[DocBlockElement], List[ObjectId]]:
        """Class method for parsing Markdown strings into DocBlockElements

        Args:
            md (str): Markdown string.
            mode (Optional[str], optional): Parsing mode as defined by Md2DocBlock constants. Defaults to GENERIC_MODE.

        Returns:
            Tuple[List[DocBlockElement], List[ObjectId]]: The first element of the tuple is a list of the parsed DocBlockElements. The second element is a list of objectId's that correspond to the highest level DocBlockElements.
        """
        parser = cls(mode_set=mode)
        token_list = parser.md_to_token(md)
        id_list = []
        for token in token_list:
            id_list.append(parser.make_block(token))

        return (parser.get_block_list(), id_list)

    @property
    def mode(self) -> str:
        """Getter for the mode of an instance of this parser.

        Returns:
            str: Mode of the parser.
        """
        return self._mode

    @mode.setter
    def mode(self, mode_to_set: str):
        """Sets the mode of the parser, modifying the function list to a specific behavior.

        Args:
            mode_to_set (str): Can be either Md2DocBlock.GENERIC_MODE or Md2DocBlock.ONE_NOTE_MODE.

        Raises:
            AttributeError: Using mode presets to configure the parse function list.
        """
        if mode_to_set == self.GENERIC_MODE:
            self._mode = self.GENERIC_MODE
            self._func_list = self._default_func_list.copy()
        elif mode_to_set == self.ONE_NOTE_MODE:
            self._func_list = self._default_func_list.copy()
            self.override_func_list(DocBlockElementType.LINK, self._on_link)
            self._mode = self.ONE_NOTE_MODE
        else:
            raise AttributeError(f"Invalid mode: {mode_to_set}")

    @property
    def func_list(self) -> Dict[str, Callable]:
        """Shallow copy of parser list.

        Returns:
            Dict[str, Callable]: A string-callable dictionary for each token type specified in Md2DocBlock.TOKEN_TYPES
        """
        return self._func_list.copy()

    @func_list.setter
    def func_list(self, set_func_list: Dict[DocBlockElementType, Callable]):
        """Sets the entire parsing function list.

        Args:
            set_func_list (Dict[DocBlockElementType, Callable]): Function list to set the parser's function list to.
        """
        self._func_list = set_func_list.copy()

    def override_func_list(self, token_parser_type: DocBlockElementType, token_parser_callable: Callable):
        """Sets the parse functions for each potential token type encountered in a markdown file.

        Args:
            token_parser_type (Optional[DocBlockElementType]): Name of the token type to override or replace
            token_parser_callable (Optional[Callable]): Callable to replace the parser for a token type of token_parser_type.

        Raises:
            AttributeError: No parser type specified to override while token_parser_callable is not None.
        """
        if not token_parser_type and token_parser_callable:
            raise AttributeError(f"No token parser type given to override with {token_parser_callable}.")
        else:
            self._func_list[token_parser_type] = token_parser_callable
            self._mode = self.USER_DEFINED_MODE

    def md_to_token(self, raw_md: str) -> List[Dict[str, Any]]:
        """Parses a raw Markdown string into python tokens.

        Args:
            raw_md (str): Raw string formatted in Markdown.

        Returns:
            List[Dict[str, Any]]: An Markdown AST generated by mistune.
        """
        bp = mistune.BlockParser(max_nested_level=10)  # Instantiate a new block parser to a predefined max nesting level
        markdown = mistune.Markdown(
            renderer=None, block=bp, plugins=[table]
        )  # renderer=None allows parsing to python tokens. Import other plugins as needed
        token_list = markdown(raw_md)

        debug_print(token_list)

        return token_list

    def get_block_list(self):
        return self.__block_list.copy()

    def make_children_blocks(self, token: Dict[str, Any]) -> List[ObjectId]:
        child_list = token.get("children")
        if not child_list:
            return []

        id_list: List[ObjectId] = []

        for child in child_list:
            id_list.append(self.make_block(child))

        return id_list

    def make_block(self, token: Dict[str, Any]) -> ObjectId:
        token_type = token.get("type")
        if token_type in self.func_list:
            try:
                new_block: DocBlockElement = self._func_list[token_type](token)
            except Exception as e:
                raise Exception(f"While parsing: {token}.") from e
        else:
            raise KeyError(f"Invalid token type: {token}")

        self.__block_list.append(new_block)
        return new_block.id

    def _text(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(type=DocBlockElementType.TEXT, block_content=token.get("raw"))

    def _emphasis(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        return DocBlockElement(type=DocBlockElementType.EMPHASIS, children=id_list)

    def _strong(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        return DocBlockElement(type=DocBlockElementType.STRONG, children=id_list)

    def _link(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        attrs = token.get("attrs")
        url = attrs.get("url") if attrs else None
        title = attrs.get("title") if attrs else None

        return DocBlockElement(
            type=DocBlockElementType.LINK,
            children=id_list,
            block_attr={"url": url, "title": title},
        )

    def _on_link(self, token: Dict[str, Any]) -> DocBlockElement:
        try:
            basename = self._on_check_relative(token)
            link_block = self._link(token)
            link_block.type = DocBlockElementType.RESOURCE_REFERENCE
            link_block.block_attr["basename"] = basename
            link_block.block_attr["type"] = token["type"]
            return link_block
        except NotRelativeURIWarning:
            return self._link(token)

    def _image(self, token: Dict[str, Any]) -> DocBlockElement:
        block = self._func_list[DocBlockElementType.LINK](token)
        if block.type == DocBlockElementType.RESOURCE_REFERENCE:
            return block
        else:
            block.type = DocBlockElementType.IMAGE
            return block

    def _codespan(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(type=DocBlockElementType.CODESPAN, block_content=token.get("raw"))

    def _line_break(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(type=DocBlockElementType.LINE_BREAK)

    def _soft_break(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(type=DocBlockElementType.SOFT_BREAK)

    def _blank_line(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(type=DocBlockElementType.BLANK_LINE)

    def _inline_html(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(type=DocBlockElementType.INLINE_HTML, block_content=token.get("raw"))

    def _paragraph(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        return DocBlockElement(type=DocBlockElementType.PARAGRAPH, children=id_list)

    def _heading(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        attrs = token.get("attrs")
        level = attrs.get("level") if attrs else None

        return DocBlockElement(type=DocBlockElementType.HEADING, children=id_list, block_attr={"level": level})

    def _thematic_break(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(type=DocBlockElementType.THEMATIC_BREAK)

    def _block_text(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        return DocBlockElement(type=DocBlockElementType.BLOCK_TEXT, children=id_list)

    def _block_code(self, token: Dict[str, Any]) -> DocBlockElement:
        raw = token.get("raw")
        attrs = token.get("attrs")
        lang = attrs.get("info") if attrs else None

        return DocBlockElement(type=DocBlockElementType.BLOCK_CODE, block_content=raw, block_attr={"language": lang})

    def _block_quote(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        return DocBlockElement(type=DocBlockElementType.BLOCK_QUOTE, children=id_list)

    def _block_html(self, token: Dict[str, Any]) -> DocBlockElement:
        return DocBlockElement(type=DocBlockElementType.BLOCK_HTML, block_content=token.get("raw"))

    def _list(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        attrs = token.get("attrs")
        ordered = attrs.get("ordered") if attrs else None
        depth = attrs.get("depth") if attrs else None
        bullet = token.get("bullet")
        tight = token.get("tight")

        return DocBlockElement(
            type=DocBlockElementType.LIST,
            children=id_list,
            block_attr={"ordered": ordered, "depth": depth, "bullet": bullet, "tight": tight},
        )

    def _list_item(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        return DocBlockElement(type=DocBlockElementType.LIST_ITEM, children=id_list)

    def _table(self, token: Dict[str, Any]) -> DocBlockElement:
        return self._table_element(token, DocBlockElementType.TABLE)

    def _table_head(self, token: Dict[str, Any]) -> DocBlockElement:
        return self._table_element(token, DocBlockElementType.TABLE_HEAD)

    def _table_body(self, token: Dict[str, Any]) -> DocBlockElement:
        return self._table_element(token, DocBlockElementType.TABLE_BODY)

    def _table_row(self, token: Dict[str, Any]) -> DocBlockElement:
        return self._table_element(token, DocBlockElementType.TABLE_ROW)

    def _table_cell(self, token: Dict[str, Any]) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        attrs = token.get("attrs")
        align = attrs.get("align") if attrs else None
        head = attrs.get("head") if attrs else None

        return DocBlockElement(type=DocBlockElementType.TABLE_CELL, block_attr={"align": align, "head": head}, children=id_list)

    def _table_element(self, token: Dict[str, Any], element: DocBlockElementType) -> DocBlockElement:
        id_list = self.make_children_blocks(token)
        return DocBlockElement(type=element, children=id_list)

    def _on_check_relative(self, token: Dict[str, Any]) -> str:
        """Checks a token for a uri, and if it is a relative reference to another item in a resource folder like in a oneNote export.

        Args:
            token (Dict[str, Any]): Token to check for a relative reference.

        Raises:
            AttributeError: Raised if the token does not have a url attribute in "attrs".
            NotRelativeURIWarning: Raised if the token does not contain a relative URI

        Returns:
            str: basename of the file.
        """
        raw_uri = token.get("attrs").get("url")

        if not raw_uri:
            raise AttributeError(f"No url field in this token: {token}.")

        path_pattern = r"^(?:\.\.\/)*resources\/(.*)$"
        match = re.match(path_pattern, raw_uri)
        if match:
            return match.group(1)
        else:
            raise NotRelativeURIWarning(f"Provided token does not contain a relative URI for a oneNote Export: {token}")


class NotRelativeURIWarning(Exception):
    """Raised if a URI is not a relative reference."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MissingBlockElements(Exception):
    def __init__(self, id: ObjectId) -> None:
        super().__init__(f"Missing block with id: {id!s}")
