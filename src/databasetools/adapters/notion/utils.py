"""
@brief
@details
@author    Mathew Cosgrove
@date      Thursday November 16th 2023
@file      utils.py
@copyright (c) 2023 NORTHROP GRUMMAN CORPORATION
-----
Last Modified: 01/09/2024 02:09:48
Modified By: Mathew Cosgrove
-----
"""

import logging
import re
import unicodedata
import uuid
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

from dateutil.parser import parse

RICH_TEXT_CONTENT_MAX_LENGTH = 2000
RICH_TEXT_LINK_MAX_LENGTH = 1000
EQUATION_EXPRESSION_MAX_LENGTH = 1000


def flatten_dict(data: Dict):
    """Remove entries in dict whose values are None"""
    if isinstance(data, dict):
        return {key: flatten_dict(value) for key, value in data.items() if value is not None}
    elif isinstance(data, list) or isinstance(data, tuple):
        return [flatten_dict(value) for value in data]
    else:
        return data


# def is_item_empty(item: Any) -> bool:

#     if item is None or item == []:
#         return True

#     isna = pd.isna(item)
#     if is_array_like(isna):
#         isna = isna.all()
#         # TODO: Rethink it is all or any

#     return isna


def is_time_string(s: str) -> bool:

    # Ref https://stackoverflow.com/questions/25341945/check-if-string-has-date-any-format
    try:
        parse(s)
        return True
    except ValueError:
        return False


def is_uuid(s: str) -> bool:
    # Kind of an OK solution.. But can be further improved?
    try:
        UUID(str(s))
        return True
    except ValueError:
        return False


ISO8601_REGEX = r"^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$"
# See https://stackoverflow.com/questions/41129921/validate-an-iso-8601-datetime-string-in-python
# ISO8601_STRFTIME_TRANSFORM = lambda ele: ele.strftime("%Y-%m-%dT%H:%M:%SZ")

# strtime_transform = lambda ele: parse(ele).strftime("%Y-%m-%dT%H:%M:%SZ")
# datetime_transform = lambda ele: ele.strftime("%Y-%m-%dT%H:%M:%SZ")


# def transform_time(s: Any) -> str:
#     if not is_item_empty(s):
#         if isinstance(s, str):
#             return strtime_transform(s)
#         elif isinstance(s, datetime):
#             return datetime_transform(s)
#         elif is_datetime64_any_dtype(s):
#             return datetime_transform(s)


# IDENTITY_TRANSFORM = lambda ele: ele
# SECURE_STR_TRANSFORM = lambda ele: str(ele) if not is_item_empty(ele) else ""
# LIST_TRANSFORM = lambda ele: ele if is_list_like(ele) else [ele]
# REMOVE_EMPTY_STR_TRANSFORM = (
#     lambda ele: None if ele == "" or ele is None or pd.isna(ele) else SECURE_STR_TRANSFORM(ele)
# )
# SECURE_BOOL_TRANSFORM = lambda ele: bool(ele) if not is_item_empty(ele) else None
# SECURE_TIME_TRANSFORM = transform_time


BASE_URL = "https://www.notion.so/"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("databasetools")


class InvalidNotionIdentifier(Exception):
    pass


def normalize_id(id: str) -> str:
    return id.replace("-", "")


def get_whitespace(line, leading=True):
    if leading:
        stripped = line.lstrip()
        return line[: -len(stripped)], stripped
    stripped = line.rstrip()
    return line[len(stripped) :], stripped


def find_title_prop(properties: Dict[str, Any]) -> Optional[str]:
    """Find Title Property.

    Args:
        properties (Dict[str, Any]): Properties Dict

    Returns:
        Optional[str]: Property ID
    """
    for name in properties:
        if properties[name]["id"] == "title":
            return name
    return None


def get_title_content(title: Dict[str, Any]) -> Optional[str]:
    """Get Title Content.

    Args:
        title (Dict[str, Any]): Title Dict

    Returns:
        str: Title Content
    """
    if "title" not in title:
        return ""
    if len(title["title"]) == 0:
        return ""
    if "text" not in title["title"][0]:
        return ""
    if "content" not in title["title"][0]["text"]:
        return ""
    return title["title"][0]["text"]["content"]


def get_page_name(page: Dict[str, Any]) -> Optional[str]:
    """Get Page Name.

    Args:
        page (Dict[str, Any]): Page Dict

    Returns:
        Optional[str]: Page Name
    """
    if "properties" not in page:
        return None

    title_prop = find_title_prop(page["properties"])
    page_name = get_title_content(page["properties"][title_prop])
    return page_name


def get_by_path(path: Union[str, List[str]], obj: Union[Dict[str, Any], List[Any]], default=None):
    """
    Get a value from a nested object using a sequence of keys.

    Args:
        path (Union[str, List[str]]): A sequence of keys to traverse down the object.
        obj (Union[Dict[str, Any], List[Any]]): The object to traverse.
        default: The default value to return if the path does not exist in the object.

    Returns:
        The value at the end of the path, or the default value if the path does not exist.
    """

    if isinstance(path, str):
        path = path.split(".")

    value = obj

    # try to traverse down the sequence of keys defined in the path, to get the target value if it exists
    try:
        for key in path:
            if isinstance(value, list):
                idx = int(key)
                value = value[idx]
            else:
                value = value[key]
    except (KeyError, TypeError, IndexError):
        value = default

    return value


def extract_id(url_or_id):
    """
    Extract the block/page ID from a Notion.so URL -- if it's a bare page URL, it will be the
    ID of the page. If there's a hash with a block ID in it (from clicking "Copy Link") on a
    block in a page, it will instead be the ID of that block. If it's already in ID format,
    it will be passed right through.
    """
    input_value = url_or_id
    if url_or_id.startswith(BASE_URL):
        url_or_id = url_or_id.split("#")[-1].split("/")[-1].split("&p=")[-1].split("?")[0].split("-")[-1]
    try:
        return str(uuid.UUID(url_or_id))
    except ValueError as e:
        logger.error(f"Failed to extract ID from {input_value}: {e}")
        raise InvalidNotionIdentifier(f"Failed to extract ID from {input_value}: {e}") from e


def extract_id_from_notion_url(notion_url: str) -> str:
    """Extract ID from Notion URL.

    Args:
        notion_url (str): Notion URL

    Returns:
        str: ID
    """
    name_uuid_str = notion_url.split("?")[0].split("/")[-1]
    return name_uuid_str.split("-")[-1]


def multi_select_from_list(keywords: List[str]) -> Dict[str, Any]:
    """Make Properties from Keywords.

    Args:
        keywords (List[str]): List of keywords.

    Returns:
        Dict[str, Any]: Properties Dict.
    """
    return {"multi_select": [{"name": keyword} for keyword in keywords]}


def slugify(original):
    """
    Slugify a unicode string.

    Example:

        >>> slugify(u"Héllø Wörld")
        u"hello-world"

    """
    original = unicodedata.normalize("NFKD", original).encode("ascii", "ignore").decode("ascii")
    original = re.sub(r"[^\w\s-]", "", original).strip().lower()
    return re.sub(r"[-\s]+", "-", original)
