import unittest
import os
import shutil
import tempfile
import mongomock

from pathlib import Path
from pprint import pprint
from bson import ObjectId

from databasetools.models.block_model import DocBlockElement, DocBlockElementType
from databasetools.adapters.oneNote.md2docBlock import Md2DocBlock, InvalidTokenError, NotRelativeURIWarning
from databasetools.adapters.oneNote.oneNote import OneNoteTools, AlreadyAttachedToDir, NotMDFileError

MONGO_URI = os.getenv("MONGO_URI")
TEST_DIR = os.getenv("TEST_DIR")

TEST_MD = '''

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

'''

class TestOneNote(unittest.TestCase):
    def setUp(self):
        # Check mongo
        if not MONGO_URI:
            raise AttributeError("MONGO_URI environment variable not set. Set it in .env")
    
        self.on_test_dir = Path(tempfile.mkdtemp())
        
        # Write test markdown file
        raw_fm = '''---\ntitle: How to own a turtle\nid: e8a544a56247455f8db120e2bfc32258\noneNoteId: '{182A7B13-941F-00A2-210B-8A28D8622AAE}{1}{E1891305927741015750620105221977488905505901}'\noneNotePath: /right/over/here\nupdated: 2022-10-18T04:53:03.0000000-07:00\ncreated: 2022-04-04T12:20:40.0000000-07:00\n---'''
        self.test_md_path = self.on_test_dir / "test_md.md"
        with open(self.test_md_path, "w") as md_file:
            md_file.write(raw_fm + TEST_MD)
        
        # Initialize tool to test
        self.on = OneNoteTools(MONGO_URI, "test_db", "test_blocks", "test_relations", "test_resources")
        
    def test_current_dir_path(self):
        assert not self.on._current_dir_path
        assert not self.on._current_dir_name
        
        self.on._current_dir_path = "this/is/a/dumb.path"
        assert self.on._current_dir_name == "dumb.path"
        assert self.on._current_dir_path == Path("this/is/a/dumb.path")
        
        with self.assertRaises(AlreadyAttachedToDir):
            self.on._current_dir_path = "replacing/current/path/when/it/is/already/defined.txt"
            
        del self.on._current_dir_path
        assert not self.on._current_dir_name
        assert not self.on._current_dir_path
        
        with self.assertRaises(AttributeError):
            self.on._current_dir_name = "this_should_not_set.poop"
        
    def test_upload_oneNote_export(self):
        pass
        
    def test_upload_md_dir(self):
        if not TEST_DIR:
            raise ValueError(f"No test directory provided. Set the test directory environment variable to point to a valid oneNote export.")
    
        # missed = self.on.upload_oneNote_export(TEST_DIR)
        
        with self.assertRaises(FileNotFoundError):
            self.on.upload_md_dir("made/up/path/hahaha/hahaha/hahahaha")
        
        
        with self.assertRaises(NotADirectoryError):
            self.on.upload_md_dir(self.test_md_path)
        
            
            
                
        
        
        
    
    def test_upload_block_list(self):
        self.on.manager.reset_collection()
        docNum = 1000
        block_list = [DocBlockElement(type=DocBlockElementType.PAGE, name=str(num)) for num in range(docNum)]
        self.on.upload_block_list(block_list)
        assert self.on.manager.blocks_collection.count_documents({}) == docNum
        
        self.on.manager.reset_collection()
    
    def test_parse_page_from_file(self):
        a_directory = self.on_test_dir / "bogus_dir"
        os.mkdir(a_directory)
        with self.assertRaises(TypeError):
            self.on.parse_page_from_file(a_directory)
        
        with self.assertRaises(FileExistsError):
            self.on.parse_page_from_file(self.on_test_dir / "boooOOOOgus_file.md")
           
        no_md_path =  self.on_test_dir / "no_md_extension.txt"
        with open(no_md_path, "w") as file:
            file.write("glub glub glub")
        with self.assertRaises(NotMDFileError):
            self.on.parse_page_from_file(no_md_path)
        
        self.on._current_dir_path = self.on_test_dir
        block_list = self.on.parse_page_from_file(self.test_md_path)
        assert block_list
        assert isinstance(block_list, list)
        for block in block_list:
            assert isinstance(block, DocBlockElement)
        page_block = block_list[0]
        assert page_block.name == "How to own a turtle"
        assert page_block.type == DocBlockElementType.PAGE
        attrs = page_block.block_attr
        assert attrs
        assert attrs["oneNote_page_id"]
        assert attrs["oneNoteId"]
        assert attrs["oneNote_created_at"]
        assert attrs["oneNote_modified_at"]
        assert attrs["oneNote_path"]
        assert attrs["export_name"] == os.path.basename(self.on_test_dir)
        assert attrs["export_relative_path"]
        
        del self.on._current_dir_path
        block_list = self.on.parse_page_from_file(self.test_md_path)
        assert block_list
        assert block_list[0].block_attr["export_name"] == None
        assert block_list[0].block_attr["export_relative_path"] == None
    
    def test_store_resources(self):
        invalid_dir = "/bogus/directory/that/cant/possibly/exist"
        with self.assertRaises(FileNotFoundError):
            self.on.store_resources(invalid_dir)
    
    def tearDown(self):
        if os.path.exists(self.on_test_dir):
            shutil.rmtree(self.on_test_dir)
        

class TestMd2DocBlock(unittest.TestCase):
    def setUp(self):
        self.parser = Md2DocBlock()
        
    def test_init(self):
        assert self.parser.func_list
        assert len(self.parser.func_list) == 18
        assert isinstance(self.parser.func_list, dict)
        assert self.parser.mode == self.parser.GENERIC_MODE
        assert self.parser.ignored_token_types == [self.parser.TOKEN_TYPES["BLANK_LINE"]]
    
    def test_mode(self):
        def_func_list = self.parser._default_func_list
        
        # Test setter:
        
        # Test setter protections
        with self.assertRaises(AttributeError):
            self.parser.mode = None
            
        with self.assertRaises(AttributeError):
            self.parser.mode = self.parser.USER_DEFINED_MODE
            
        # Check that function list is set correctly
        self.parser.mode = self.parser.GENERIC_MODE 
        assert self.parser.mode == self.parser.GENERIC_MODE
        general_func_list = self.parser.func_list
        for name in def_func_list:
            assert def_func_list[name] == general_func_list[name]        
        
        # Check changing modes sets function list correctly
        self.parser.mode = self.parser.ONE_NOTE_MODE
        assert self.parser.mode == self.parser.ONE_NOTE_MODE
        on_func_list = self.parser.func_list
        for name in def_func_list:
            if name != DocBlockElementType.LINK and name != DocBlockElementType.IMAGE:
                assert def_func_list[name] == on_func_list[name]
        assert def_func_list[DocBlockElementType.LINK] != on_func_list[DocBlockElementType.LINK]
        assert def_func_list[DocBlockElementType.IMAGE] != on_func_list[DocBlockElementType.IMAGE]
        assert on_func_list[DocBlockElementType.LINK] == self.parser._on_link
        assert on_func_list[DocBlockElementType.IMAGE] == self.parser._on_image
        
        # Test Getter:
        
        # Ensure getter protects _mode attr
        cur_mode = self.parser.mode
        cur_mode = "BOGUS"
        assert cur_mode != self.parser.mode
        
    def test_func_list(self):
        self.parser.mode = self.parser.GENERIC_MODE
        
        # Test getter:
        
        # Test getter protects _func_list
        def_func_list = self.parser._default_func_list
        func_list = self.parser.func_list
        func_list.clear()
        
        for name in def_func_list:
            assert self.parser._func_list[name] == def_func_list[name]
            
        # Test setter:
        
        # Test setting
        new_func_list = self.parser.func_list
        for name in new_func_list:
            new_func_list[name] = None
            
        self.parser.func_list = new_func_list
        
        for name in self.parser._func_list:
            assert self.parser._func_list[name] == None
            
        # Test setter protects _func_list
        def foo(): pass
        
        for name in new_func_list:
            new_func_list[name] = foo
            
        for name in self.parser._func_list:
            assert self.parser._func_list[name] == None
            
    def test_override_func(self):
        self.parser.mode = self.parser.GENERIC_MODE
        
        def foo(): pass
        self.parser.override_func_list(DocBlockElementType.LINK, foo)
        assert self.parser.func_list[DocBlockElementType.LINK] == foo
        
        with self.assertRaises(AttributeError):
            self.parser.override_func_list(None, foo)
        
        self.parser.override_func_list(DocBlockElementType.LINK, None)
        assert self.parser.func_list[DocBlockElementType.LINK] == None    
        
    def test_trim_tokens(self):
        # Test getter protections
        tt = self.parser.ignored_token_types
        assert len(tt) == 1
        
        tt.append("Hello there!")
        assert len(self.parser.ignored_token_types) == 1
        
        # Test setter protections
        tt = ["hi!"]
        self.parser.ignored_token_types = tt
        assert len(self.parser.ignored_token_types) == 2 # Should be two elements since we always ignore blank line types
        
        tt.append("some junk")
        assert len(self.parser.ignored_token_types) == 2
        assert self.parser.ignored_token_types[0] == "hi!"
        
        self.parser.ignored_token_types = None
        assert len(self.parser.ignored_token_types) == 1 # Defaults to ignore blank lines
        
    def test_add_ignored_types(self):
        test_list = ["t1", "t2", "t3"]
        self.parser.add_ignored_types(test_list)
        assert len(self.parser._ignored_token_types) == 4
        
        test_list[0] = "t0"
        result_ignored_list = self.parser.ignored_token_types
        for item in result_ignored_list:
            assert item != "t0"
            
        self.parser.ignored_token_types = None
        
    def test_remove_ignored_types(self):
        self.parser.remove_ignored_types([self.parser.TOKEN_TYPES["BLANK_LINE"]])
        assert len(self.parser._ignored_token_types) == 0
        
        self.parser.ignored_token_types = None
        assert len(self.parser.ignored_token_types) == 1
        
        self.parser.remove_ignored_types(self.parser.TOKEN_TYPES["BLANK_LINE"])
        assert len(self.parser._ignored_token_types) == 0
        
        # make sure it don't do nothing if removing types that are not present
        self.parser.remove_ignored_types(["attempting", "to", "remove", "types", "not", "in", "list"])
        
    def test_md_to_token(self):
        token_list = self.parser.md_to_token(TEST_MD)
        assert token_list
        self.assertIsInstance(token_list, list)
        for item in token_list:
            self.assertIsInstance(item, dict)
            self.assertNotEqual(item.get("type"), "blank_line")
            self.assertNotEqual(item.get("type"), None)
            
        # pprint(token_list, sort_dicts=False)
        
    def test_text(self):
        test_text = {
            "type": "text",
            "raw": "Hello this is normal text!"
        }
        result = self.parser._text(test_text)
        assert result
        assert isinstance(result, DocBlockElement)
        assert result.type == "text"
        
        null_input = {
            "type": "text",
            "raw": ""
        }
        null_result = self.parser._text(null_input)
        assert not null_result # Should still make block but empty
        
    def test_heading(self):
        heading_test = {
            'type': 'heading',
            'attrs': {
                'level': 1
            },
            'style': 'axt',
            'children': [
                    {
                        'type': 'text', 
                        'raw': 'Heading 1'
                    }
            ]
        }
        result = self.parser._heading(heading_test)
        assert result
        self.assertIsInstance(result, DocBlockElement)
        self.assertEqual(result.type, "heading")
        self.assertDictEqual(result.block_attr, {"level": 1})
        self.assertEqual(result.block_content, "Heading 1")
        self.assertIsNotNone(result.id)
        
        invalid_heading = {
            'type': 'heading',
            'attrs': {
                'level': 3
            },
            'style': 'axt',
            'children': [
                {
                    'type': 'block_code',
                    'raw': 'Some codespan text'
                }, 
                {
                    'type': 'text',
                    'raw': 'Hellooooooo'
                }
            ]
        }
        self.assertRaises(InvalidTokenError, self.parser._heading, invalid_heading)

    def test_block_code(self):
        test_block_code = {
            "type": "block_code",
            "raw": "from peanuts import Peanuts\npeanuts = Peanuts()\npeanuts.roast()\npeanuts.make_peanutbutter()\n",
            "style": "fenced",
            "marker": "'''",
            "attrs": {
                "info": "python"
            }
        }
        result = self.parser._block_code(test_block_code)
        assert result
        self.assertIsInstance(result, DocBlockElement)
        self.assertIsInstance(result.block_content, str)
        assert result.type == "block_code"

    def test_codespan(self):
        test_codespan = {
            "type": "codespan",
            "raw": "import this"
        }
        result = self.parser._codespan(test_codespan)
        assert result
        assert isinstance(result, DocBlockElement)
        assert result.type == "codespan"
        assert result.block_content == "import this"
        
        empty_codespan = {
            "type": "codespan",
            "raw": ""
        }
        null_result = self.parser._codespan(empty_codespan)
        assert not null_result
        
    def test_image(self):
        test_image = {
            "type": "image",
            "children": [
                {"type": "text", "raw": "This should be an image!"}
            ],
            "attrs": {"url": "image_url"}
        }
        result = self.parser._image(test_image)
        assert result
        assert isinstance(result, DocBlockElement)
        assert result.block_attr["url"]
        assert result.block_content == "This should be an image!"
        
        invalid_image = {
            "type": "image",
            "children": [
                {"type": "text", "raw": "This should be an image!"},
                {"type": "block_quote", "raw": "bogus code"}
            ],
            "attrs": {"url": "image_url"}
        }
        self.assertRaises(InvalidTokenError, self.parser._image, invalid_image)
        
    def test_on_image(self):
        on_image_token = {
            "type": "image",
            "children": [
                {"type": "text", "raw": "An image to a relatively referenced image."}
            ],
            "attrs": {"url": "../../../resources/gecko.jpg"}
        }
        result = self.parser._on_image(on_image_token)
        assert result
        assert result.type == DocBlockElementType.RESOURCE_REFERENCE
        assert result.status == "Unverified"
        assert len(result.block_attr) == 2
        assert result.block_attr.get("filename")
        assert result.block_attr.get("extension")
        
        regular_image_token = {
            "type": "image",
            "children": [
                {"type": "text", "raw": "This should be an image!"}
            ],
            "attrs": {"url": "image_url"}
        }
        reg_result = self.parser._on_image(regular_image_token)
        assert reg_result
        assert reg_result.type == DocBlockElementType.IMAGE
        
        weird_image_token = {
            "type": "image",
            "children": [
                {"type": "text", "raw": "An image to a relatively referenced image."}
            ],
            "attrs": {"url": "../../../resources/gecko_no_extension"}
        }
        weird_result = self.parser._on_image(weird_image_token)
        assert weird_result
        assert weird_result.type == DocBlockElementType.RESOURCE_REFERENCE
        
    def test_link(self):
        test_link = {
            "type": "link",
            "children": [
                {
                    "type": "text",
                    "raw": "link with a "
                },
                {
                    "type": "strong",
                    "children": [
                        {
                            "type": "text",
                            "raw": "STRONG LINK"
                        }
                    ]
                },
                {"type": "linebreak"},
                {
                    "type": "image",
                    "children": [
                        {"type": "text", "raw": "Image here"}
                    ],
                    "attrs": {"url": "image_url_here"}
                }
            ],
            "attrs":{
                "url": "Hello_url"
            }
        }
        result = self.parser._link(test_link)
        assert result
        assert len(result) == 3
        assert result[0].block_attr["url"] == "Hello_url"
        assert result[0].block_content == "link with a **STRONG LINK**\nImage here"
        assert len(result[0].children) == 2
        
    def test_on_link(self):
        test_on_link = {
            "type": "link",
            "children": [
                {
                    "type": "text",
                    "raw": "link with a "
                },
                {
                    "type": "strong",
                    "children": [
                        {
                            "type": "text",
                            "raw": "STRONG LINK"
                        }
                    ]
                },
                {"type": "linebreak"},
                {
                    "type": "image",
                    "children": [
                        {"type": "text", "raw": "Image here"}
                    ],
                    "attrs": {"url": "../../../../../resources/238023948j203948r.jpg"}
                }
            ],
            "attrs":{
                "url": "../../../../resources/23874923749723.hello"
            }
        }
        self.parser.mode = self.parser.ONE_NOTE_MODE
        
        result = self.parser._on_link(test_on_link)
        assert result
        assert len(result) == 3
        found_relative_references = 0
        for item in result:
            if item.type != "resource_reference":
                continue
            else:
                assert len(item.block_attr) == 2
                assert isinstance(item.block_attr.get("filename"), str)
                assert isinstance(item.block_attr.get("extension"), str)
                assert item.status == "Unverified"
                found_relative_references += 1
        assert found_relative_references == 2
        
        self.parser.mode = self.parser.GENERIC_MODE
        
            
    def test_paragraph(self):
        test_paragraph = {
            "type": "paragraph",
            "children": [
                {'type': 'text', 'raw': 'Here is a '},
                {'type': 'text', 'raw': '**BOLD**'},
                {'type': 'text', 'raw': '. Here is an '},
                {'type': 'text', 'raw': '*Italic*'},
                {'type': 'text', 'raw': ' and here is a '},
                {'type': 'text', 'raw': '***BOLD and Italic***'},
                {'type': 'linebreak'},
                {'type': "text", 'raw': 'This is on a new line.'},
                {'type': 'softbreak'},
                {'type': "text", 'raw': 'This is on the same line.'},
                {'type': 'linebreak'},
                {'type': 'linebreak'},
                {'type': 'linebreak'},
                {'type': "text", 'raw': 'This is on a new line.'}
            ]
        }
        test_paragraph_key = "Here is a **BOLD**. Here is an *Italic* and here is a ***BOLD and Italic***\nThis is on a new line. This is on the same line.\n\n\nThis is on a new line."
        result = self.parser._paragraph(test_paragraph)
        assert result
        assert len(result) == 2
        assert result[0].block_content == test_paragraph_key
        test_paragraph["children"].append(
            {
                "type": "link",
                "children": [
                    {
                        "type": "text",
                        "raw": "link with a "
                    },
                    {
                        "type": "strong",
                        "children": [
                            {
                                "type": "text",
                                "raw": "STRONG LINK"
                            }
                        ]
                    },
                    {"type": "linebreak"},
                    {
                        "type": "image",
                        "children": [
                            {"type": "text", "raw": "Image here"}
                        ],
                        "attrs": {"url": "image_url_here"}
                    }
                ],
                "attrs":{
                    "url": "Hello_url"
                }
            }
        )
        
        result_2 = self.parser._paragraph(test_paragraph)
        assert result_2
        assert len(result_2) == 5
        
        test_paragraph_2 = {
            "type": "paragraph",
            "children": [
                {
                    "type": "text",
                    "raw": "content here"
                },
                {
                    "type": "linebreak"
                },
                {
                    "type": "codespan",
                    "raw": "heres a code span"
                }
            ]
        }
        
        result_3 = self.parser._paragraph(test_paragraph_2)
        assert result_3
        assert len(result_3) == 2
        
    def test_block_text(self):
        test_block_text = {
            'type': 'block_text',
            'children': [
                {'type': 'text','raw': 'List item 1'}
            ]
        }
        result = self.parser._block_text(test_block_text)
        assert result
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].type == "block_text"
        
    def test_block_quote(self):
        test_quote = {
            "type": "block_quote",
            "children": [
                {
                    'type': 'block_code',
                    'raw': 'import Hello\nHello.say()\n',
                    'style': 'fenced',
                    'marker': '```',
                    'attrs': {'info': 'python'}
                },
                {
                    'type': 'paragraph',
                    'children': [
                        {'type': 'codespan','raw': 'Here is a code block'}
                    ]
                },
                {
                    'type': 'paragraph',
                    'children': [
                        {'type': 'text', 'raw': 'Here is a quote. Its not that long.'},
                        {'type': 'linebreak'},
                        {'type': 'text', 'raw': 'Here is a break!'},
                        {'type': 'softbreak'},
                        {'type': 'text','raw': 'This should be part of the quote.'}
                    ]
                },
                {
                    "type": "block_quote",
                    "children": [
                        {"type": "text", "raw": "Nested quotes"}
                    ]
                }
            ]
        }
        result = self.parser._block_quote(test_quote)
        assert result
        assert isinstance(result, list)
        assert len(result) == 8
        for item in result:
            assert isinstance(item, DocBlockElement)
        
    def test_list_item(self):
        test_list_item = {
            'type': 'list_item',
            'children': [
                {
                    'type': 'block_text',
                    'children': [
                        {
                            'type': 'text',
                            'raw': 'Sublist item 1'
                        }
                    ]
                }
            ]
        }
        result = self.parser._list_item(test_list_item)
        assert result
        assert len(result) == 3
        assert result[0].type == "list_item"
        
    def test_list(self):
        test_list = {
            'type': 'list',
            'children': [
                {
                    'type': 'list_item',
                    'children': [
                        {
                            'type': 'block_text',
                            'children': [
                                {
                                    'type': 'text',
                                    'raw': 'List item 1'
                                }
                            ]
                        },
                        {
                            'type': 'list',
                            'children': [
                                {
                                    'type': 'list_item',
                                    'children': [
                                        {
                                            'type': 'block_text',
                                            'children': [
                                                {
                                                    'type': 'text',
                                                    'raw': 'Sublist item 1'}
                                            ]
                                        }
                                    ]
                                },
                                {
                                    'type': 'list_item',
                                    'children': [
                                        {
                                            'type': 'block_text',
                                            'children': [
                                                {
                                                    'type': 'text',
                                                    'raw': 'Sublist item 2'
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ],
                            'tight': True,
                            'bullet': '.',
                            'attrs': {'depth': 1, 'ordered': True}
                        }
                    ]
                },
                {
                    'type': 'list_item',
                    'children': [
                        {
                            'type': 'block_text',
                            'children': [
                                {
                                    'type': 'text',
                                    'raw': 'List item 2'
                                }
                            ]
                        }
                    ]
                },
                {
                    'type': 'list_item',
                    'children': [
                        {
                            'type': 'block_text',
                            'children': [
                                {
                                    'type': 'text',
                                    'raw': 'List item 3'
                                }
                            ]
                        }
                    ]
                }
            ],
            'tight': True,
            'bullet': '.',
            'attrs': {'depth': 0, 'ordered': True}
        }
        
        result = self.parser._list(test_list)
        assert result
        assert isinstance(result, list)
        assert len(result) == 17
        valid_types = ["list", "list_item", "block_text", "text"]
        for item in result:
            assert item.type in valid_types
            if item.type == "list_item" or item.type == "list":
                assert item.block_content == None
        assert result[0].block_attr["ordered"] == True
        assert result[0].block_attr["depth"] == 0
        
    def test_make_table_element(self):
        null_result = self.parser._make_table_element(None, DocBlockElementType.TABLE)
        assert null_result
        assert len(null_result) == 1
        assert null_result[0].type == DocBlockElementType.TABLE
        
    def test_table(self):
        test_table = {'type': 'table',
  'children': [{'type': 'table_head',
                'children': [{'type': 'table_cell',
                              'attrs': {'align': None, 'head': True},
                              'children': [{'type': 'text', 'raw': 'Here'}]},
                             {'type': 'table_cell',
                              'attrs': {'align': None, 'head': True},
                              'children': [{'type': 'text', 'raw': 'Is'}]},
                             {'type': 'table_cell',
                              'attrs': {'align': None, 'head': True},
                              'children': [{'type': 'text', 'raw': 'A'}]},
                             {'type': 'table_cell',
                              'attrs': {'align': None, 'head': True},
                              'children': [{'type': 'text', 'raw': 'Table'}]}]},
               {'type': 'table_body',
                'children': [{'type': 'table_row',
                              'children': [{'type': 'table_cell',
                                            'attrs': {'align': None,
                                                      'head': False},
                                            'children': [{'type': 'text',
                                                          'raw': 'A'}]},
                                           {'type': 'table_cell',
                                            'attrs': {'align': None,
                                                      'head': False},
                                            'children': [{'type': 'text',
                                                          'raw': 'B'}]},
                                           {'type': 'table_cell',
                                            'attrs': {'align': None,
                                                      'head': False},
                                            'children': [{'type': 'text',
                                                          'raw': 'C'}]},
                                           {'type': 'table_cell',
                                            'attrs': {'align': None,
                                                      'head': False},
                                            'children': [{'type': 'text',
                                                          'raw': 'D'}]}]},
                             {'type': 'table_row',
                              'children': [{'type': 'table_cell',
                                            'attrs': {'align': None,
                                                      'head': False},
                                            'children': [{'type': 'text',
                                                          'raw': 'A'}]},
                                           {'type': 'table_cell',
                                            'attrs': {'align': None,
                                                      'head': False},
                                            'children': [{'type': 'text',
                                                          'raw': 'B'}]},
                                           {'type': 'table_cell',
                                            'attrs': {'align': None,
                                                      'head': False},
                                            'children': [{'type': 'text',
                                                          'raw': 'C'}]},
                                           {'type': 'table_cell',
                                            'attrs': {'align': None,
                                                      'head': False},
                                            'children': [{'type': 'text',
                                                          'raw': 'D'}]}]}]}]}
        
        result = self.parser._table(test_table)
        assert result
        assert isinstance(result, list)
        assert len(result) == 29
        valid_types = ["table", "table_cell", "table_row", "table_head", "table_body", "text"]
        for item in result:
            assert item.type in valid_types
    
    def test_block_html(self):
        block_html_token = {
            'type': 'block_html',
            'raw': '<colgroup>\n<col style="width: 21%" />\n<col style="width: 78%" />\n</colgroup>\n'
        }
        result = self.parser._block_html(block_html_token)
        assert result 
        assert result.type == DocBlockElementType.BLOCK_HTML
        assert result.block_content
        
    def test_strip_inline_HTML(self):
        test_list = [
            {'type': 'text', 'raw': 'Here is a paragraph with a inline HTML element for a '},
            {'type': 'inline_html', 'raw': '<sup>'},
            {'type': 'text', 'raw': 'superscript!'},
            {'type': 'inline_html', 'raw': '</sup>'},
            {'type': 'text', 'raw': ' Wowza!'}
        ]
        result = self.parser._strip_inline_HTML(test_list)
        assert len(result) == 5
        for item in result:
            assert item["type"] != self.parser.TOKEN_TYPES["INLINE_HTML"]
            
    def test_get_children_block_elements(self):
        null_result = self.parser._get_children_block_elements({"type": "text"})
        assert null_result
        assert not null_result[0]
        assert not null_result[1]
        assert not null_result[2]
        
    def test_remove_elements_of_type(self):
        test_token_list = [
            {"type": "text", "raw": "Hello There"},
            {"type": "paragraph", "children": [
                {"type": None},
                {"type": "text", "raw": "Dont remove me!"}
            ]},
            {"type": "block_quote", "children": [
                {"type": "text", "raw": "Nested quotes"},
                {"type": "block_quote", "children": [
                    {"type": "text", "raw": "Nested quotes"},
                    {"type": "block_quote", "children": [
                        {"type": "text", "raw": "Nested quotes"},
                        {"type": "block_quote", "children": [
                            {"type": "text", "raw": "Nested quotes"},
                            {"type": None},
                            {"type": "blank_line"}
                        ]}
                    ]}
                ]}
            ]}
        ]
        
        result = self.parser._remove_elements_of_type(test_token_list, self.parser._ignored_token_types)
        block_list = self.parser.make_blocks(result)
        for block in block_list:
            assert block.type != None
            assert block.type != self.parser.TOKEN_TYPES["BLANK_LINE"]
            
    def test_token_list2str(self):
        test_token_list = [
            {"type": "text", "raw": "Hello There"},
            {"type": "linebreak"},
            {"type": "paragraph", "children": [
                {"type": "text", "raw": "Dont remove me!"},
                {"type": "softbreak"}
            ]},
            {"type": "block_quote", "children": [
                {"type": "text", "raw": "Nested quotes"},
                {"type": "linebreak"},
                {"type": "block_quote", "children": [
                    {"type": "text", "raw": "doubly nested quotes"},
                    {"type": "linebreak"},
                    {"type": "block_quote", "children": [
                        {"type": "text", "raw": "triply nested quotes"},
                        {"type": "softbreak"},
                        {"type": "block_quote", "children": [
                            {"type": "text", "raw": "Nested quotes"},
                            {"type": "softbreak"}
                        ]}
                    ]}
                ]}
            ]}
        ]
        answer = "Hello There\nDont remove me! Nested quotes\ndoubly nested quotes\ntriply nested quotes Nested quotes "
        result = self.parser._token_list2str(test_token_list)
        assert result
        assert isinstance(result, str)
        assert result == answer
        
    def test_simplify_token_list(self):
        test_tokens = [
            {"type": "codespan", "raw": "some codespan content"}
        ]
        answer = "`some codespan content`"
        result = self.parser._simplify_token_list(test_tokens)
        assert len(result) == 1
        assert result[0]["type"] == self.parser.TOKEN_TYPES["TEXT"]
        assert result[0]["raw"] == answer
        
        test_tokens.extend([
            {"type": "linebreak"},
            {"type": "strong", "children": [
                {"type": "text", "raw": "some strong text"}
            ]}]
        )
        answer += "\n**some strong text**"
        result = self.parser._simplify_token_list(test_tokens)
        assert len(result) == 1
        assert result[0]["type"] == self.parser.TOKEN_TYPES["TEXT"]
        assert result[0]["raw"] == answer
        
        test_tokens.extend([
            {"type": "softbreak"},
            {"type": "strong", "children": [
                {"type": "emphasis", "children": [
                    {"type": "text", "raw": "strong emphasis"}
                ]}
            ]}
        ])
        answer += " ***strong emphasis***"
        result = self.parser._simplify_token_list(test_tokens)
        assert len(result) == 1
        assert result[0]["type"] == self.parser.TOKEN_TYPES["TEXT"]
        assert result[0]["raw"] == answer
        
        test_tokens.extend([
            {"type": "linebreak"},
            {"type": "inline_html", "raw": "<sup>"},
            {"type": "text", "raw": "superscript text using html!"},
            {"type": "inline_html", "raw": "</sup>"}
        ])
        answer += "\n<sup>superscript text using html!</sup>"
        result = self.parser._simplify_token_list(test_tokens)
        assert len(result) == 1
        assert result[0]["type"] == self.parser.TOKEN_TYPES["TEXT"]
        assert result[0]["raw"] == answer

        test_tokens.extend([
            {"type": "thematic_break"},
            {"type": "paragraph", "children": [
                {"type": "text", "raw": "Hello!"},
                {"type": "linebreak"}
            ]}
        ])
        result = self.parser._simplify_token_list(test_tokens)
        assert len(result) == 3
        
    def test_on_check_relative(self):
        test_token = {
            "type": "link",
            "raw": "hello there!",
            "attrs": {
                "url": "../../../../../resources/hello.txt"
            }
        }
        filename_result, extension_result = self.parser._on_check_relative(test_token)
        assert filename_result == "hello"
        assert extension_result == ".txt"
        
        test_token["attrs"]["url"] = "../resources/no_extension"
        filename_result, null_extension_result = self.parser._on_check_relative(test_token)
        assert filename_result == "no_extension"
        assert not null_extension_result
        
        test_token["attrs"]["url"] = "http://google.com/"
        self.assertRaises(NotRelativeURIWarning, self.parser._on_check_relative, test_token)
        