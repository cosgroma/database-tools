import unittest
import unittest.test

import mistune

from databasetools.models.docblock import DocBlockElementType
from databasetools.utils.docBlock.docBlock_utils import FromDocBlock
from databasetools.utils.docBlock.docBlock_utils import ToDocBlock

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
| ---: | :--- | :---: | --- |
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
>>>>>> Helloooooooooo
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

Here is a relative ![LINK](../../resources/hello.jpg)

[1]: Hello

"""


class TestDocBlock2Md(unittest.TestCase):
    def test_docblock2md(self):
        block_list, id_list = ToDocBlock.parse_md2docblock(TEST_MD)

        convert_result, required_resources = FromDocBlock.render_docBlock(block_list, id_list)  # Testing This!

        html_convert_result = mistune.html(convert_result)
        assert html_convert_result
        assert isinstance(html_convert_result, str)

        renderer = mistune.HTMLRenderer(escape=False)
        html_result, _ = FromDocBlock.render_docBlock(block_list, id_list, renderer)
        html_answer = mistune.html(TEST_MD)

        assert isinstance(html_answer, str)
        assert html_answer == html_result
        assert not required_resources

        block_list, id_list = ToDocBlock.parse_md2docblock(TEST_MD, ToDocBlock.ONE_NOTE_MODE)

        convert_result, required_resources = FromDocBlock.render_docBlock(block_list, id_list, resource_prefix="hello")  # Testing This!

        html_convert_result = mistune.html(convert_result)
        assert isinstance(html_convert_result, str)
        assert required_resources
        assert len(required_resources) == 1
        assert "hello/hello.jpg" in html_convert_result
        truncated_result = "\n".join(html_convert_result.split("\n")[0:-2])
        html_answer = "\n".join(html_answer.split("\n")[0:-2])
        assert html_answer == truncated_result


class TestMd2DocBlock(unittest.TestCase):
    def test_md2docblock(self):
        block_list, id_list = ToDocBlock.parse_md2docblock(TEST_MD, mode=ToDocBlock.ONE_NOTE_MODE)
        assert block_list
        assert id_list

        type_list = [block.type for block in block_list]

        assert DocBlockElementType.RESOURCE_REFERENCE in type_list
