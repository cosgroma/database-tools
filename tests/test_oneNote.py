import unittest
from pprint import pprint


from databasetools.models.block_model import DocBlockElement, DocBlockElementType
from databasetools.adapters.oneNote.type_parsing import Md2DocBlock, NotMDFileError, InvalidTokenError

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

I should be a seperate paragraph.  
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

Here is a paragraph but I will be embeding a `code block` in it.

This paragraph contains a [reference Link][1]

[![Here is an **image** with a link](image_url)](link_url)

Here is a paragraph with a inline HTML element for a <sup>superscript!</sup> Wowza!

<colgroup>
<col style="width: 21%" />
<col style="width: 78%" />
</colgroup>

[1]: Hello

'''

TEST_REMOVE_BOLD_EMPHASIS = [
    {
        'type': 'text', 
        'raw': 'Here is a '
    },
    {
        'type': 'strong', 
        'children': [
                {
                    'type': 'text', 
                    'raw': 'BOLD'
                }
            ]
    },
    {
        'type': 'text', 
        'raw': '. Here is an '
    },
    {
        'type': 'emphasis',
        'children': [
                {
                    'type': 'text', 
                    'raw': 'Italic'
                }
            ]
    },
    {
        'type': 'text', 
        'raw': ' and here is a '
    },
    {
        'type': 'emphasis',
        'children': [
            {
                'type': 'strong',
                'children': [
                    {
                        'type': 'text',
                        'raw': 'BOLD and Italic'
                    }
                ]
            }
        ]
    }
]

class TestTypeParsing(unittest.TestCase):
    def setUp(self):
        self.parser = Md2DocBlock()
        
    def test_set_export_mode(self):
        self.parser.reset()
        
        orig_funcs = [func for func in self.parser.func_list.values()] # Collect original functions
        self.parser.set_export_mode(self.parser.ONE_NOTE_MODE)
        
        assert self.parser.export_mode == self.parser.ONE_NOTE_MODE
        diff_count = 0
        for func in orig_funcs:
            if func not in self.parser.func_list.values():
                diff_count += 1

        assert diff_count == 2
        
        self.parser.set_export_mode(self.parser.GENERIC_MODE)
        
        for func in orig_funcs:
            assert func in self.parser.func_list.values()
            
    def test_set_parser(self):
        self.parser.reset()
        
        self.parser.func_list = None
        assert self.parser.func_list == None
        
        self.parser.set_parser()
        assert self.parser.func_list
        
        def foo():
            pass
        
        self.assertRaises(AttributeError, self.parser.set_parser, None, foo)
        
        self.parser.set_parser(DocBlockElementType.TEXT, foo)
        assert self.parser.func_list[DocBlockElementType.TEXT] == foo 
        
    def test_process_page(self):
        no_md_path = "/thing/there/hello/file/file_with_no_md"
        self.assertRaises(NotMDFileError, self.parser.process_page, no_md_path)
        
        md_path = no_md_path + ".md"
        self.assertRaises(FileNotFoundError, self.parser.process_page, md_path)
        
    def test_md_to_token(self):
        token_list = self.parser.md_to_token(TEST_MD)
        assert token_list
        self.assertIsInstance(token_list, list)
        for item in token_list:
            self.assertIsInstance(item, dict)
            self.assertNotEqual(item.get("type"), "blank_line")
            self.assertNotEqual(item.get("type"), None)
            
        # pprint(token_list, sort_dicts=False)
    
    def test_make_block(self):
        invalid_input = {
            "type": "poopoo", 
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
        self.assertRaises(KeyError, self.parser.make_block, invalid_input)
        
        null_result = self.parser.make_block(None)
        assert not null_result
        
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
        self.parser.set_export_mode("one_note")
        result = self.parser._on_link(test_on_link)
        assert result
        assert len(result) == 3
        found_reletive_references = 0
        for item in result:
            if item.type != "resource_reference":
                continue
            else:
                assert len(item.block_attr) == 2
                assert isinstance(item.block_attr.get("filename"), str)
                assert isinstance(item.block_attr.get("extension"), str)
                assert item.status == "Unverified"
                found_reletive_references += 1
        assert found_reletive_references == 2
        self.parser.set_export_mode("generic")
        
            
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
            
    def _test_combine_text(self):
        combine_text_testObj = [
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
        result = self.parser._combine_text(combine_text_testObj)
        invalid_types = ["linebreak", "softbreak", "codespan"]
        assert result
        assert isinstance(result, list)
        assert len(result) == 1
        for item in result:
            assert isinstance(item, dict)
            assert isinstance(item.get("raw"), str)
            assert item["type"] not in invalid_types

        input_2 = combine_text_testObj + [{"type": "paragraph", "raw": "hello"}]
        result_2 = self.parser._combine_text(input_2)
        assert result_2
        assert len(result_2) == 2
        
    def _test_remove_bold_emphasis(self): 
        stripped = self.parser._remove_bold_emphasis(TEST_REMOVE_BOLD_EMPHASIS)
        assert stripped
        self.assertIsInstance(stripped, list)
        for item in stripped:
            self.assertIsInstance(item, dict)
            assert item.get("type")
            assert item.get("raw")
            self.assertNotEqual(item.get("type"), "strong")
            self.assertNotEqual(item.get("type"), "emphasis")
            
    
        


    




