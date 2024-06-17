from typing import Any
from typing import Dict
from typing import List
from typing import Optional

BLOCK_TYPES = (
    "bookmark",
    "breadcrumb",
    "bulleted_list_item",
    "callout",
    "child_database",
    "child_page",
    "column",
    "column_list",
    "divider",
    "embed",
    "equation",
    "file",
    "heading_1",
    "heading_2",
    "heading_3",
    "image",
    "link_preview",
    "link_to_page",
    "numbered_list_item",
    "paragraph",
    "pdf",
    "quote",
    "synced_block",
    "table",
    "table_of_contents",
    "table_row",
    "template",
    "to_do",
    "toggle",
    "unsupported",
    "video",
)

# blocks = [
#     {
#         "paragraph": {"rich_text": [{"text": {"content": "I'm a paragraph."}}]}
#     },
#     {
#         "heading_2": {"rich_text": [{"text": {"content": "I'm a heading."}}]}
#     },
#     {
#         "bulleted_list_item": {
#             "rich_text": [{"text": {"content": "I'm a bulleted list."}}]
#         }
#     },
#     {
#         "numbered_list_item": {
#             "rich_text": [{"text": {"content": "I'm a numbered list."}}]
#         }
#     },
#     {
#         "to_do": {
#             "rich_text": [{"text": {"content": "I'm a to-do list."}}],
#             "checked": False,
#         }
#     },
#     {
#         "toggle": {
#             "rich_text": [{"text": {"content": "I'm a toggle list."}}],
#             "children": [
#                 {
#                     "paragraph": {
#                         "rich_text": [{"text": {"content": "I'm a child block."}}]
#                     }
#                 }
#             ],
#         }
#     },
#     {
#         "quote": {
#             "rich_text": [{"text": {"content": "I'm a quote."}}],
#             "children": [
#                 {
#                     "paragraph": {
#                         "rich_text": [{"text": {"content": "I'm a child block."}}]
#                     }
#                 }
#             ],
#         }
#     }
# ]


# "paragraph": {
#     "rich_text": [
#         {
#             "type": "text",
#             "text": {
#                 "content": "COL 2",
#                 "link": null
#             },
#             "annotations": {
#                 "bold": true,
#                 "strikethrough": false,
#                 "underline": false,
#                 "code": false,
#                 "color": "default"
#             },
#             "plain_text": "COL 2",
#             "href": null
#         }
#     ],
#     "color": "default"
# },


def create_rich_text(
    text: str,
    link: Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    underline: bool = False,
    code: bool = False,
    color: str = "default",
) -> Dict[str, Any]:
    return [
        {
            "type": "text",
            "text": {"content": text, "link": link},
            "annotations": {
                "bold": bold,
                "italic": italic,
                "strikethrough": strikethrough,
                "underline": underline,
                "code": code,
                "color": color,
            },
            "plain_text": text,
            "href": None,
        }
    ]


class RichText:
    def __init__(
        self,
        text: str,
        link: Optional[str] = None,
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        color: str = "default",
    ) -> None:
        self.text = text
        self.link = link
        self.bold = bold
        self.italic = italic
        self.strikethrough = strikethrough
        self.underline = underline
        self.code = code
        self.color = color

    def set_annotations(
        self,
        bold: bool = False,
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
        code: bool = False,
        color: str = "default",
    ) -> None:
        self.bold = bold
        self.italic = italic
        self.strikethrough = strikethrough
        self.underline = underline
        self.code = code
        self.color = color

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "text",
            "text": {"content": self.text, "link": self.link},
            "annotations": {
                "bold": self.bold,
                "italic": self.italic,
                "strikethrough": self.strikethrough,
                "underline": self.underline,
                "code": self.code,
                "color": self.color,
            },
            "plain_text": self.text,
            "href": None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RichText":
        text = data["text"]["content"]
        link = data.get("link", None)
        bold = data.get("annotations", {}).get("bold", False)
        italic = data.get("annotations", {}).get("italic", False)
        strikethrough = data.get("annotations", {}).get("strikethrough", False)
        underline = data.get("annotations", {}).get("underline", False)
        code = data.get("annotations", {}).get("code", False)
        color = data.get("annotations", {}).get("color", "default")
        return cls(text, link, bold, italic, strikethrough, underline, code, color)


class Block:
    def __init__(self, type: str, rich_text: Dict[str, Any], color: str = "default") -> None:
        self.type = type
        self.rich_text = RichText.from_dict(rich_text)
        self.color = color
        self.has_children = False
        self.children: List[Block] = []

    def set_rich_text(self, rich_text: RichText) -> None:
        self.rich_text = rich_text

    def add_child(self, block: "Block") -> None:
        self.children.append(block)

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.type: {
                "rich_text": self.rich_text.to_dict(),
                "color": self.color,
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        type = next(iter(data.keys()))
        if data["has_children"]:
            children = [cls.from_dict(child) for child in data["children"]]
        rich_text = RichText.from_dict(data[type]["rich_text"])
        color = data[type]["color"]
        block = cls(type, rich_text, color)
        for child in children:
            block.add_child(child)
        return block


def create_paragraph_block(
    text: str,
    color: str = "default",
    link: Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    underline: bool = False,
    code: bool = False,
) -> Dict[str, Any]:
    return {"paragraph": {"rich_text": create_rich_text(text, link, bold, italic, strikethrough, underline, code, color), "color": color}}


# {
#     "object": "block",
#     "has_children": false,
#     "type": "heading_2",
#     "heading_2": {
#         "rich_text": [
#             {
#                 "type": "text",
#                 "text": {
#                     "content": "Projects",
#                     "link": null
#                 },
#                 "annotations": {
#                     "bold": false,
#                     "italic": false,
#                     "strikethrough": false,
#                     "underline": false,
#                     "code": false,
#                     "color": "default"
#                 },
#                 "plain_text": "Projects",
#                 "href": null
#             }
#         ],
#         "is_toggleable": false,
#         "color": "default"
#     },
#     "children": []
# },


def create_heading_block(
    text: str,
    level: int = 1,
    link: Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    underline: bool = False,
    code: bool = False,
    color: str = "default",
    toggleable: bool = False,
) -> dict:
    if level not in (1, 2, 3):
        raise ValueError("Level must be 1, 2, or 3")
    return {
        f"heading_{level}": {
            "rich_text": create_rich_text(text, link, bold, italic, strikethrough, underline, code, color),
            "is_toggleable": toggleable,
            "color": color,
        }
    }


def create_list_block(
    items: List[str],
    numbered: bool = False,
    link: Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    underline: bool = False,
    code: bool = False,
    color: str = "default",
) -> dict:
    if numbered:
        type = "numbered_list_item"
    else:
        type = "bulleted_list_item"
    return [{type: {"rich_text": create_rich_text(text, link, bold, italic, strikethrough, underline, code, color)}} for text in items]


def create_to_do_block(
    text: List[str],
    checked: Optional[List[bool]] = None,
    link: Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    underline: bool = False,
    code: bool = False,
    color: str = "default",
) -> dict:
    if checked is None:
        checked = [False] * len(text)
    if len(text) != len(checked):
        raise ValueError("Length of text and checked must be the same")
    return [
        {
            "to_do": {
                "rich_text": create_rich_text(item, link, bold, italic, strikethrough, underline, code, color),
                "checked": check,
            }
        }
        for item, check in zip(text, checked)
    ]


# {
#         "to_do": {
#             "rich_text": create_rich_text(text, link, bold, italic, strikethrough, underline, code, color),
#             "checked": checked,
#         }
#     }


def create_quote_block(
    text: str,
    children: Optional[List[Dict[str, Any]]] = None,
    link: Optional[str] = None,
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    underline: bool = False,
    code: bool = False,
    color: str = "default",
) -> dict:
    return {
        "quote": {
            "rich_text": create_rich_text(text, link, bold, italic, strikethrough, underline, code, color),
            "children": children or [],
        }
    }


def create_code_block(text: str, language: str = "") -> Dict[str, Any]:
    return {
        "code": {
            "language": language,
            "rich_text": [{"type": "text", "text": {"content": text}}],
        }
    }


def create_embed_block(url: str) -> Dict[str, Any]:
    return {"embed": {"url": url}}


def create_toggle_block(text: str, children: Optional[List[Dict[str, Any]]] = None) -> dict:
    return {
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "children": children or [],
        }
    }


def create_divider_block() -> dict:
    return {"divider": {}}


def create_table_block(rows: List[List[str]], headers: Optional[List[str]] = None) -> dict:
    return {
        "table": {
            "rows": [{"cells": [{"text": [{"type": "text", "text": {"content": cell}}]} for cell in row]} for row in rows],
            "headers": [{"text": [{"type": "text", "text": {"content": header}}]} for header in headers or []],
        }
    }


def create_breadcrumb_block(items: List[Dict[str, str]]) -> dict:
    return {"breadcrumb": {"items": [{"text": [{"type": "text", "text": {"content": item["content"]}}]} for item in items]}}


def create_callout_block(icon: str, text: str) -> dict:
    return {"callout": {"icon": icon, "rich_text": [{"type": "text", "text": {"content": text}}]}}


def create_link_to_page_block(page_id: str) -> dict:
    return {"link_to_page": {"page_id": page_id}}


def create_table_of_contents_block() -> dict:
    return {"table_of_contents": {}}
