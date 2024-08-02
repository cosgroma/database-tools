import os
import unittest
from pathlib import Path

from bson import ObjectId

from databasetools.adapters.oneNote.oneNote import OneNoteTools
from databasetools.models.docblock import DocBlockElement
from databasetools.models.docblock import PageElement
from databasetools.models.docblock import PageTypes

test_env = os.getenv("TEST_DIR")
assert test_env, "TEST_DIR not set. Set it in .env file"
TEST_DIR = Path(test_env)


class TestOneNote(unittest.TestCase):
    def test_init(self):
        on = OneNoteTools(TEST_DIR)
        assert on.root_path == Path(TEST_DIR)
        assert isinstance(on.export_id, ObjectId)
        assert on._resource_path == Path(TEST_DIR) / "resources"
        assert on._export_path.exists()
        assert on._md_file_list
        dupe_list = []
        key = [Path(on._export_path, file) for file in Path.glob("**", root_dir=on._export_path, recursive=True)]
        key.append(on._export_path)
        for item in on._md_file_list:
            item_path = Path(on._export_path, item)
            assert item_path.exists()
            assert item_path not in dupe_list
            dupe_list.append(item_path)

            assert item_path in key

        for item in on._folder_list:
            item_path = Path(on._export_path, item)
            assert item_path in key

        for item in on._missed_files:
            item_path = Path(on._export_path, item)
            assert item_path.exists()
            assert item_path.suffix != ".md"

        assert len(on._md_file_list) + len(on._folder_list) == len(key)

    def test_folder_page_gen(self):
        on = OneNoteTools(TEST_DIR)
        assert isinstance(on.folder_page_len(), int)
        folder_id_key = [on._folder_list[folder] for folder in on._folder_list]
        page_id_key = [on._md_file_list[file] for file in on._md_file_list]
        name_key = [Path(folder).name for folder in on._folder_list]
        for pageElement in on.folder_page_gen():
            assert isinstance(pageElement, PageElement)
            assert pageElement.id in folder_id_key
            assert pageElement.type == PageTypes.FOLDER
            assert pageElement.name in name_key
            for folder_id in pageElement.sub_folders:
                assert folder_id in folder_id_key
            for child_id in pageElement.children:
                assert child_id in page_id_key
            assert pageElement.export_name
            assert pageElement.export_id
            assert (on._export_path / pageElement.relative_path).exists()

    def test_file_page_gen(self):
        on = OneNoteTools(TEST_DIR)
        assert isinstance(on.file_page_len(), int)
        for file_element, block_list, resource_list in on.file_page_gen():
            assert isinstance(file_element, PageElement)
            assert isinstance(block_list, list)
            assert isinstance(resource_list, list)

            assert file_element.type == PageTypes.PAGE
            assert file_element.id == on._md_file_list[Path(on._export_path, file_element.relative_path)]
            assert isinstance(file_element.children, list)
            assert isinstance(file_element.name, str)
            assert file_element.created_at
            assert file_element.modified_at
            assert file_element.export_name
            assert file_element.export_id
            assert file_element.relative_path

            id_list = [docblock.id for docblock in block_list]
            for child_id in file_element.children:
                assert child_id in id_list

            for block in block_list:
                assert isinstance(block, DocBlockElement)
                assert block.export_id == file_element.export_id

            for resource in resource_list:
                assert resource.exists()
