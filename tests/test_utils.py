from pprint import pprint

from databasetools.adapters.notion import utils
from databasetools.utils.md import md_utils

# def flatten_dict(data: Dict):
# def is_time_string(s: str) -> bool:
# def is_uuid(s: str) -> bool:
# def normalize_id(id: str) -> str:
# def get_whitespace(line, leading=True):
# def find_title_prop(properties: Dict[str, Any]) -> Optional[str]:
# def get_title_content(title: Dict[str, Any]) -> Optional[str]:
# def get_page_name(page: Dict[str, Any]) -> Optional[str]:
# def get_by_path(path: Union[str, List[str]], obj: Union[Dict[str, Any], List[Any]], default=None):
# def extract_id(url_or_id):
# def extract_id_from_notion_url(notion_url: str) -> str:
# def multi_select_from_list(keywords: List[str]) -> Dict[str, Any]:
# def slugify(original):

# def test_flatten_dict():
#     data = {
#         "key1": "value1",
#         "key2": {
#             "key3": "value3",
#             "key4": {
#                 "key5": "value5",
#             },
#         },
#     }
#     expected = { "key1": "value1", "key2.key3": "value3", "key2.key4.key5": "value5" }
#     assert utils.flatten_dict(data) == expected


def test_is_time_string():
    assert utils.is_time_string("2022-01-01T00:00:00Z")
    assert utils.is_time_string("2022-01-01T00:00:00")
    assert utils.is_time_string("2022-01-01")
    assert utils.is_time_string("2022-01")
    assert not utils.is_time_string("Not Date")


def test_is_uuid():
    assert utils.is_uuid("01234567-89ab-cdef-0123-456789abcdef")
    assert not utils.is_uuid("01234567-89ab-cdef-0123-456789abcde")


def test_normalize_id():
    assert utils.normalize_id("01234567-89ab-cdef-0123-456789abcdef") == "0123456789abcdef0123456789abcdef"


def test_get_whitespace():
    assert utils.get_whitespace("   test") == ("   ", "test")
    assert utils.get_whitespace("test   ") == ("", "test   ")


def test_find_title_prop():
    properties = {
        "title": {
            "id": "title",
        },
    }
    assert utils.find_title_prop(properties) == "title"


# def test_get_title_content():
#     title = {
#         "title": [
#             {
#                 "text": {
#                     "content": "Test",
#                 },
#             },
#         ],
#     }
#     assert utils.get_title_content(title) == "Test"

# def test_get_page_name():
#     page = {
#         "properties": {
#             "title": {
#                 "id": "title",
#                 "title": [
#                     {
#                         "text": {
#                             "content": "Test",
#                         },
#                     },
#                 ],
#             },
#         },
#     }
#     assert utils.get_page_name(page) == "Test"


def test_get_by_path():
    obj = {
        "key1": {
            "key2": {
                "key3": "value3",
            },
        },
    }
    assert utils.get_by_path("key1.key2.key3", obj) == "value3"


# def test_extract_id():
#     url_or_id = "https://www.notion.so/0123456789abcdef0123456789abcdef"
#     assert utils.extract_id(url_or_id) == "0123456789abcdef0123456789abcdef"


# def test_extract_id_from_notion_url():
#     notion_url = "https://www.notion.so/0123456789abcdef0123456789abcdef"
#     assert utils.extract_id_from_notion_url(notion_url) == "0123456789abcdef0123456789abcdef"


def test_slugify():
    test_string = "Héllø Wörld"
    expected = "hell-world"
    assert utils.slugify(test_string) == expected


def test_markdown_utils():
    test_string = """
Lorem ipsum
```python
print('foo```bar```foo')
print('foo```bar```foo')
```
Lorem ipsum
```python
print('foo```bar```foo')
print('foo```bar```foo')
```
Lorem ipsum
```
print('foo```bar```foo')
print('foo```bar```foo')
```
"""
    code_blocks = md_utils.get_code_blocks(test_string)
    # print(code_blocks)
    for code_block in code_blocks:
        pprint(code_block)
