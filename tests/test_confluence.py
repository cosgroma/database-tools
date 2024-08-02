import os
import unittest
from pprint import pprint

from databasetools.adapters.confluence.confluence import ConfluenceManager

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

TEST_DIR = os.getenv("TEST_DIR")
TEST_DB_NAME = "test_db"
TEST_DB_COL_NAME = "test_db_col"
TEST_GRID_NAME = "test_grid"
TEST_CON_COL_NAME = "test_confluence_col"


class TestConfluence(unittest.TestCase):
    def setUp(self):
        # proxies = {"http": HTTP_PROXY, "https": HTTPS_PROXY} if HTTPS_PROXY and HTTPS_PROXY else None
        self.con_man = ConfluenceManager(
            confluence_url=CONFLUENCE_URL,
            confluence_space_key=CONFLUENCE_SPACE_KEY,
            confluence_username=CONFLUENCE_UNAME,
            confluence_api_token=CONFLUENCE_TOKEN,
        )

    def test_ty(self):
        thing = self.con_man.make_confluence_page_directory("bob")
        pprint(thing, sort_dicts=False)
