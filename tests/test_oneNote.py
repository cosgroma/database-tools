import os
import secrets
import shutil
import tempfile
import unittest
from pathlib import Path

import pytest

from databasetools.adapters.oneNote.oneNote import AlreadyAttachedToDir
from databasetools.adapters.oneNote.oneNote import NotMDFileError
from databasetools.adapters.oneNote.oneNote import NotOneNoteExport
from databasetools.adapters.oneNote.oneNote import OneNoteTools
from databasetools.models.block_model import DocBlockElement
from databasetools.models.block_model import DocBlockElementType

MONGO_URI = os.getenv("MONGO_URI")
TEST_DIR = os.getenv("TEST_DIR")

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

TEST_FM = """
---
title: How to own a turtle
id: e8a544a56247455f8db120e2bfc32258
oneNoteId: '{182A7B13-941F-00A2-210B-8A28D8622AAE}{1}{E1891305927741015750620105221977488905505901}'
oneNotePath: /right/over/here
updated: 2022-10-18T04:53:03.0000000-07:00
created: 2022-04-04T12:20:40.0000000-07:00
---
"""


class TestOneNote(unittest.TestCase):
    def setUp(self):
        # Check mongo
        if not MONGO_URI:
            raise AttributeError("MONGO_URI environment variable not set. Set it in .env")

        self.on_test_dir = Path(tempfile.mkdtemp())

        # Write test markdown file
        self.test_md_path = self.on_test_dir / "test_md.md"
        with self.test_md_path.open("w") as md_file:
            md_file.write(TEST_FM + TEST_MD)

        # Initialize tool to test
        self.on = OneNoteTools(MONGO_URI, "test_db", "test_blocks", "test_gridFS")

    def test_current_dir_path(self):
        assert not self.on._current_dir_path
        assert not self.on._current_dir_name

        self.on._current_dir_path = "this/is/a/dumb.path"
        assert self.on._current_dir_name == "dumb.path"
        assert self.on._current_dir_path == Path("this/is/a/dumb.path")

        with pytest.raises(AlreadyAttachedToDir):
            self.on._current_dir_path = "replacing/current/path/when/it/is/already/defined.txt"

        del self.on._current_dir_path
        assert not self.on._current_dir_name
        assert not self.on._current_dir_path

    def test_upload_oneNote_export(self):
        """
        Still needs to test nested folders
        """
        docblocks_per_test_doc = len(self.on._parse_page_from_file(self.test_md_path))

        # Clean mongo
        self.on._manager.reset_collection()
        self.on._manager.reset_resources()

        # Clean test dir
        self.test_md_path.unlink()
        assert len(os.listdir(self.on_test_dir)) == 0

        # Check if no directory in export folder
        with pytest.raises(NotOneNoteExport):
            self.on.upload_oneNote_export(self.on_test_dir)

        # Test having three directories in export folder
        export_name = "salsa_export"
        export_dir = self.on_test_dir / export_name
        export_dir.mkdir()
        Path(str(export_dir) + "_1").mkdir()
        Path(str(export_dir) + "_2").mkdir()

        assert len(os.listdir(self.on_test_dir)) == 3
        with pytest.raises(NotOneNoteExport):
            self.on.upload_oneNote_export(self.on_test_dir)

        shutil.rmtree(str(export_dir) + "_1")
        shutil.rmtree(str(export_dir) + "_2")

        # Test with two directories with no resources folder
        bogus_dir_name = "bologna"
        (self.on_test_dir / bogus_dir_name).mkdir()
        with pytest.raises(FileExistsError):
            self.on.upload_oneNote_export(self.on_test_dir)
        shutil.rmtree(self.on_test_dir / bogus_dir_name)

        # Test with one directory
        invalid_file = "poopoo.txt"
        with (export_dir / invalid_file).open("x"):
            pass
        missed_files = self.on.upload_oneNote_export(self.on_test_dir)
        assert len(missed_files) == 1
        (export_dir / invalid_file).unlink()

        # Test with two directories one of which is a resources folder
        resource_dir = self.on_test_dir / "resources"
        resource_dir.mkdir()
        assert len(os.listdir(self.on_test_dir)) == 2
        assert len(os.listdir(resource_dir)) == 0
        assert len(os.listdir(export_dir)) == 0

        # Make some test md files
        total_count = 20
        valid_count = 0
        invalid_count = 0
        valid_names = []
        for i in range(total_count):
            if secrets.randbits(1):
                valid_count += 1
                filename = "valid_file_" + str(i) + ".md"
                valid_names.append(filename)
                with (export_dir / filename).open("w") as f:
                    f.write(TEST_FM + TEST_MD)
            else:
                invalid_count += 1
                filename = "invalid_file_" + str(i) + ".poopoo"
                with (export_dir / filename).open("x"):
                    pass
        missed_files = self.on.upload_oneNote_export(self.on_test_dir)
        assert self.on._manager._docblock_col.count_documents({}) == valid_count * docblocks_per_test_doc
        assert len(missed_files) == invalid_count
        self.on._manager.reset_collection()

        # Make some resource files
        resource_count = 20
        for i in range(resource_count):
            filename = "resource_" + str(i) + ".txt"
            with (resource_dir / filename).open("w") as f:
                f.write("Hello!")

        self.on.upload_oneNote_export(self.on_test_dir)
        assert self.on._manager._docblock_col.count_documents({}) == valid_count * docblocks_per_test_doc
        assert self.on._manager._gridFS_db.get_collection("fs.files").count_documents({}) == resource_count

        # Check page blocks for relative paths
        page_list = self.on._manager.find_blocks(type=DocBlockElementType.PAGE)
        assert len(page_list) == valid_count
        for page in page_list:
            assert page.block_attr["export_name"] == export_name
            assert page.block_attr["export_relative_path"] in valid_names

        # Clean Mongo
        self.on._manager.reset_collection()
        self.on._manager.reset_resources()

    def test_upload_md_dir(self):
        with pytest.raises(FileNotFoundError):
            self.on.upload_md_dir("made/up/path/hahaha/hahaha/hahahaha")

        with pytest.raises(NotADirectoryError):
            self.on.upload_md_dir(self.test_md_path)

        initial_doc_count = len(os.listdir(self.on_test_dir))

        # Make valid documents:
        valid_doc_num = 20
        for i in range(valid_doc_num):
            filename = "valid_file_" + str(i) + ".md"
            with (self.on_test_dir / filename).open("w") as f:
                f.write(TEST_FM + TEST_MD)

        # Make some invalid_docs:
        invalid_doc_num = 5
        for i in range(invalid_doc_num):
            filename = "invalid_file_" + str(i) + ".txt"
            with (self.on_test_dir / filename).open("w") as f:
                f.write(TEST_FM + TEST_MD)

        missed_files = self.on.upload_md_dir(self.on_test_dir)
        docblock_count_per_test_file = len(self.on._parse_page_from_file(self.test_md_path))
        docblock_count_mongo = self.on._manager._docblock_col.count_documents({})
        assert len(missed_files) == invalid_doc_num
        assert docblock_count_mongo == (valid_doc_num + initial_doc_count) * docblock_count_per_test_file

        self.on._manager.reset_collection()

    def test_upload_block_list(self):
        self.on._manager.reset_collection()
        docNum = 1000
        block_list = [DocBlockElement(type=DocBlockElementType.PAGE, name=str(num)) for num in range(docNum)]
        self.on._upload_block_list(block_list)
        assert self.on._manager._docblock_col.count_documents({}) == docNum

        self.on._manager.reset_collection()

    def test_parse_page_from_file(self):
        a_directory = self.on_test_dir / "bogus_dir"
        a_directory.mkdir()
        with pytest.raises(TypeError):
            self.on._parse_page_from_file(a_directory)

        with pytest.raises(FileExistsError):
            self.on._parse_page_from_file(self.on_test_dir / "boooOOOOgus_file.md")

        no_md_path = self.on_test_dir / "no_md_extension.txt"
        with (no_md_path).open("w") as file:
            file.write("glub glub glub")
        with pytest.raises(NotMDFileError):
            self.on._parse_page_from_file(no_md_path)

        self.on._current_dir_path = self.on_test_dir
        block_list = self.on._parse_page_from_file(self.test_md_path)
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
        assert attrs["export_name"] == self.on_test_dir.name
        assert attrs["export_relative_path"]

        del self.on._current_dir_path
        block_list = self.on._parse_page_from_file(self.test_md_path)
        assert block_list
        assert block_list[0].block_attr["export_name"] is None
        assert block_list[0].block_attr["export_relative_path"] is None

    def test_store_resources(self):
        invalid_dir = "/bogus/directory/that/cant/possibly/exist"
        with pytest.raises(FileNotFoundError):
            self.on.store_resources(invalid_dir)

    def tearDown(self):
        if self.on_test_dir.exists():
            shutil.rmtree(self.on_test_dir)


class TestFullUpload(unittest.TestCase):
    def setUp(self):
        if not MONGO_URI:
            raise AttributeError("MONGO_URI environment variable not set. Set it in .env")
        self.db_name = "Full_Export_Test_DB"
        self.gridFS_name = "Full_Export_Test_DB_GridFS"
        self.on = OneNoteTools(db_uri=MONGO_URI, db_name=self.db_name, gridfs_name=self.gridFS_name)

    def _test_full_export(self):
        if not TEST_DIR:
            raise AttributeError("TEST_DIR environment variable not set. Set it in .env to point to a onenote export.")
        self.on._manager.reset_collection()
        self.on._manager.reset_resources()
        missed_files = self.on.upload_oneNote_export(TEST_DIR)
        assert len(missed_files) == 0
