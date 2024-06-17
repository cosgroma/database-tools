from pathlib import Path
from pprint import pprint

from databasetools.adapters.notion import utils
from databasetools.utils.md import md_utils
from databasetools.utils.md.md_utils import MarkdownManager

USER_HOME = Path.home()
MD_DIR = Path.home() / ".ngira" / "notebooks" / "pgm Notebook-20240120 15-29" / "pgm Notebook" / "Trade Study" / "Brassboard"


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
    for code_block in code_blocks:
        pprint(code_block)

    # assert code_blocks[0] == "print('foo```bar```foo')\nprint('foo```bar```foo')\n"
    # assert code_blocks[1] == "print('foo```bar```foo')\nprint('foo```bar```foo')\n"
    # assert code_blocks[2] == "print('foo```bar```foo')\nprint('foo```bar```foo')\n"
    # assert len(code_blocks) == 3


def _test_markdown_manager():
    mm = MarkdownManager(MD_DIR)
    elements = mm.extract_elements()
    mm.save_to_json(MD_DIR / "elements.json")
    assert len(elements) > 0


def test_markdown_manager_parse_markdown_text():
    mm = MarkdownManager()
    markdown_text = """
# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6

- Unordered list item 1
- Unordered list item 2
- Unordered list item 3

1. Ordered list item 1
2. Ordered list item 2
3. Ordered list item 3

[Link to Google](https://www.google.com)

![Alt text](https://www.google.com)


| Header 1 | Header 2 |
| --- | --- |
| Row 1, Col 1 | Row 1, Col 2 |
| Row 2, Col 1 | Row 2, Col 2 |

```python
print('foo')
```

"""
    renderer = mm.parse_markdown(markdown_text)
    elements = renderer.elements
    assert len(elements) > 0

    for element in elements:
        pprint(element)

    assert elements[0]["type"] == "heading"
    assert elements[0]["level"] == 1
    assert elements[0]["content"] == "Heading 1"

    assert elements[1]["type"] == "heading"
    assert elements[1]["level"] == 2
    assert elements[1]["content"] == "Heading 2"

    assert elements[2]["type"] == "heading"
    assert elements[2]["level"] == 3
    assert elements[2]["content"] == "Heading 3"

    assert elements[3]["type"] == "heading"
    assert elements[3]["level"] == 4
    assert elements[3]["content"] == "Heading 4"

    assert elements[4]["type"] == "heading"
    assert elements[4]["level"] == 5
    assert elements[4]["content"] == "Heading 5"

    assert elements[5]["type"] == "heading"
    assert elements[5]["level"] == 6
    assert elements[5]["content"] == "Heading 6"

    assert elements[6]["type"] == "list"
    assert elements[6]["list_type"] == "unordered"
    assert elements[6]["content"] == "<li>Unordered list item 1</li>\n<li>Unordered list item 2</li>\n<li>Unordered list item 3</li>\n"

    assert elements[7]["type"] == "list"
    assert elements[7]["list_type"] == "ordered"
    assert elements[7]["content"] == "<li>Ordered list item 1</li>\n<li>Ordered list item 2</li>\n<li>Ordered list item 3</li>\n"

    assert elements[8]["type"] == "link"
    assert elements[8]["url"] == "https://www.google.com"
    assert elements[8]["title"] is None
    assert elements[8]["content"] == "Link to Google"

    assert elements[9]["type"] == "image"
    assert elements[9]["url"] == "https://www.google.com"
    assert elements[9]["alt_text"] is None
    assert elements[9]["text"] == "Alt text"

    # assert elements[10]["type"] == "table"
    # assert elements[10]["content"] == "<table><thead><tr><th>Header 1</th><th>Header 2</th></tr></thead><tbody><tr><td>Row 1, Col 1</td><td>Row 1, Col 2</td></tr><tr><td>Row 2, Col 1</td><td>Row 2, Col 2</td></tr></tbody></table>"

    # assert len(elements) == 11


def test_word_frequency():
    text = "The quick brown fox jumps over the lazy dog. The quick brown fox jumps over the lazy dog."
    mm = MarkdownManager()
    word_freq = mm.word_frequency(text)
    assert word_freq["the"] == 4
    assert word_freq["quick"] == 2
    assert word_freq["brown"] == 2
    assert word_freq["fox"] == 2
    assert word_freq["jumps"] == 2
    assert word_freq["over"] == 2
    assert word_freq["lazy"] == 2
    assert word_freq["dog"] == 2


def test_get_tables_from_text():
    text = """
# Table 1

| Name | Date | Amount |
|------|------|--------|
| John | 1/1/2022 | $100 |
| Jane | 1/2/2022 | $200 |

# Table 2

| Name | Date | Amount |
|------|------|--------|
| John | 3/1/2022 | $400 |
| Jane | 4/2/2022 | $400 |
    """
    mm = MarkdownManager()
    tables = mm.get_tables_from_text(text)
    assert len(tables) == 2
    assert (
        tables[0]
        == """| Name | Date | Amount |
|------|------|--------|
| John | 1/1/2022 | $100 |
| Jane | 1/2/2022 | $200 |"""
    )
    assert (
        tables[1]
        == """| Name | Date | Amount |
|------|------|--------|
| John | 3/1/2022 | $400 |
| Jane | 4/2/2022 | $400 |"""
    )
