import os
import tempfile
import unittest
from pathlib import Path

import mistune
from requests.exceptions import HTTPError

from databasetools.adapters.confluence.confluence import ConfluenceManager
from databasetools.models.docblock import DocBlockElement
from databasetools.models.docblock import DocBlockElementType

TEST_MD = """

# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6

Here is a **BOLD**. Here is an *Italic* and here is a ***BOLD and Italic***

```python
from peanuts import Peanuts
peanuts = Peanuts()
peanuts.roast()
peanuts.make_peanutbutter()
```

- Here is a list
  - I should be a sublist
  - I am also a sublist
- I am not a sublist
- I am also not a sublist
  - I am a sub list again
    - I am a sub-sub list.

This is finally a normal paragraph.
This should be part of the same paragraph.

I should be a separate paragraph.
I should be in the same paragraph on a different line.

| Here | Is | A | Table |
| --- | --- | --- | --- |
| A | B | C | D |
| A | B | C | D |

1. List item 1
    1. Sublist item 1
    1. Sublist item 2
1. List item 2
1. List item 3

![This should be an image!](image_url)

---
---

Here is a [LINK](a_link)

Here is a [link with a ***bold*** in it](another_link_)

> Here is a quote. Its not that long.
Here is a break!
This should be part of the quote.
>> Nested Quote!
>>>>>>> Helloooooooooo
>
> `Here is a code block`
>
> ```python
> import Hello
> Hello.say()
> ```
>
>```html
><!DOCTYPE html>
><html lang="en">
><head>
>    <title>My Simple Page</title>
></head>
><body>
>    <h1>Welcome to My Webpage</h1>
></body>
></html>
>```

Here is a paragraph but I will be embedding a `code block` in it.

This paragraph contains a [reference Link][1]

[![Here is an **image** with a link](image_url)](link_url)

Here is a paragraph with a inline HTML element for a <sup>superscript!</sup> Wowza!

<colgroup>
<col style="width: 21%" />
<col style="width: 78%" />
</colgroup>

**This is a some text with <sup>inline HTML</sup> and a [LINK](http://google.com/).

[1]: Hello

"""

HTTP_PROXY = os.getenv("HTTP_PROXY")
HTTPS_PROXY = os.getenv("HTTPS_PROXY")
CONFLUENCE_UNAME = os.getenv("CONFLUENCE_UNAME")
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")
CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")


class TestConfluence(unittest.TestCase):
    def setUp(self):
        # proxies = {"http": HTTP_PROXY, "https": HTTPS_PROXY} if HTTPS_PROXY and HTTPS_PROXY else None
        self.con_man = ConfluenceManager(
            mongo_uri=MONGO_URI,
            confluence_url=CONFLUENCE_URL,
            confluence_space_key=CONFLUENCE_SPACE_KEY,
            confluence_username=CONFLUENCE_UNAME,
            confluence_api_token=CONFLUENCE_TOKEN,
            mongo_docblock_db_name="Full_Export_Test_DB",
            mongo_docblock_collection_name="blocks",
            mongo_gridFS_db_name="Full_Export_Test_DB_GridFS",
        )

        try:
            self.con_man.make_confluence_page_directory("Test Page")
        except HTTPError:
            print("Test Page already exists")

        self.main_page = self.con_man.get_confluence_page_id("Test Page")

    def test_make_page(self):
        content = mistune.html(TEST_MD)
        self.con_man.make_confluence_page("test_md", content, self.main_page)

    def test_get_mongo_page_ids(self):
        results = self.con_man.get_mongo_page_blocks()
        for item in results:
            assert isinstance(item, DocBlockElement)
            assert item.type == DocBlockElementType.PAGE

    def test_upload_pages(self):
        page_blocks = self.con_man.get_mongo_page_blocks()[0:20]
        self.con_man.upload_pages(page_blocks)

    def test_add_confluence_attachment(self):
        temp_dir = Path(tempfile.mkdtemp())
        test_name = "003635cb420941afacda1cf27caa921c"
        file = self.con_man.mongo_man.fs_find_file(filename=test_name)
        tempf_name = test_name + ".jpg"
        tempf = Path(temp_dir / tempf_name)
        with tempf.open("wb") as f:
            f.write(file.read())

        self.con_man.add_confluence_attachments(temp_dir, self.main_page)

        for item in os.listdir(temp_dir):
            (temp_dir / item).unlink()
        temp_dir.rmdir()
