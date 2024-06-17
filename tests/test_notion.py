# exporter = NotionExporter(token=token)
# path = exporter.export_url(url=url)
# print(f" * Exported to {path}")

import json
import logging
import os
from datetime import datetime
from pathlib import Path

import pytz
from notion_objects import Checkbox
from notion_objects import Date
from notion_objects import MultiSelect
from notion_objects import Number
from notion_objects import Page
from notion_objects import Status
from notion_objects import Text
from notion_objects import TitleText

from databasetools import NotionBlock
from databasetools import NotionClient
from databasetools import NotionDatabase
from databasetools import NotionPage
from databasetools.adapters.notion import utils

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
PAGE_URL = os.getenv("PAGE_URL")
TEST_DATABASE_ID = os.getenv("TEST_DATABASE_ID")
PAGE_ID = os.getenv("PAGE_ID")

# enable all logging


logging.basicConfig(level=logging.DEBUG)


def test_client():
    # Make test directory
    assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"

    client = NotionClient(token=NOTION_API_KEY)
    assert client

    # Test get_blocks
    blocks = client.get_blocks(block_id=PAGE_ID)
    assert blocks
    assert len(blocks) > 0
    assert isinstance(blocks, list)

    # Test get_metadata
    metadata = client.get_metadata(page_id=PAGE_ID)
    assert metadata
    assert isinstance(metadata, dict)

    # Test get_recent_pages
    recent_pages = client.get_recent_pages()
    assert recent_pages
    assert len(recent_pages) > 0
    assert isinstance(recent_pages, list)

    # Test get_database
    database = client.get_database(database_id=TEST_DATABASE_ID)
    assert database
    assert len(database) > 0
    assert isinstance(database, list)


# exporter = NotionExporter(token=NOTION_API_KEY)


# def test_exporter_export_url():
#     # Make test directory
#     assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
#     assert PAGE_URL, "PAGE_URL not set, set it in .env file"
#     assert TEST_DATABASE_ID, "TEST_DATABASE_ID not set, set it in .env file"

#     test_page_name = "test_page_url"
#     json_dir = f"{test_page_name}/json"
#     md_dir = f"{test_page_name}/md"
#     json_path = Path(json_dir)
#     md_path = exporter.export_url(url=PAGE_URL, json_dir=json_dir, md_dir=md_dir)
#     assert md_path.exists()
#     assert md_path.is_file()
#     assert md_path.suffix == ".md"

#     # assert len(os.listdir(md_path)) > 0
#     assert json_path.exists()
#     assert json_path.is_dir()
#     shutil.rmtree(test_page_name)


# def test_exporter_export_page():
#     test_page_name = "test_page"
#     test_page_dir = Path(f"output/{test_page_name}")
#     if Path.exists(test_page_dir):
#         shutil.rmtree(test_page_dir)
#     json_dir = Path(f"{test_page_name}/json")
#     md_dir = Path(f"{test_page_name}/md")
#     md_path = exporter.export_page(page_id=PAGE_ID, json_dir=json_dir, md_dir=md_dir)
#     json_path = Path(json_dir)
#     assert md_path.is_file()
#     assert md_path.suffix == ".md"
#     assert json_path.exists()
#     assert json_path.is_dir()


TEST_PLANNING_PAGE_URL = "https://www.notion.so/cosgroma/Planning-for-product-development-cb0163c37cca49848345104644b544d9?pvs=4"

# class Page(NotionObject):
#     id: str = Id()
#     created_time: datetime = RootProperty()
#     last_edited_time: datetime = RootProperty()


def _test_notion_save_planning_page():
    # Make test directory
    assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
    assert TEST_PLANNING_PAGE_URL, "TEST_PLANNING_PAGE_URL not set, set it in .env file"
    int_page = NotionPage(token=NOTION_API_KEY, page_id=PAGE_ID)
    page, page_results = int_page.get_page()
    assert page
    assert page_results
    page_id_no_dash = page.id.replace("-", "")
    assert PAGE_ID == page_id_no_dash
    # assert page.properties
    blocks = int_page.get_blocks()
    assert blocks
    assert len(blocks) > 0

    child_pages = int_page.get_child_pages()
    assert child_pages
    assert len(child_pages) > 0

    for child_page in child_pages:
        if "Planning" in child_page.title:
            ...
            # planning_page_dir = Path("output/planning_page")
            # if Path.exists(planning_page_dir):
            #     shutil.rmtree(planning_page_dir)
            # json_dir = f"{planning_page_dir}/json"
            # md_dir = f"{planning_page_dir}/md"
            # md_path = exporter.export_page(page_id=child_page.page_id, json_dir=json_dir, md_dir=md_dir)
            # json_path = Path(json_dir)
            # assert md_path.is_file()
            # assert md_path.suffix == ".md"
            # assert json_path.exists()
            # assert json_path.is_dir()


def test_notion_page():
    # Make test directory
    assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
    assert TEST_PLANNING_PAGE_URL, "TEST_PLANNING_PAGE_URL not set, set it in .env file"
    # page_id = extract_id_from_notion_url(TEST_PLANNING_PAGE_URL)
    # page_id = NotionPage.get_page_id_from_url(url=TEST_PLANNING_PAGE_URL)
    int_page = NotionPage(token=NOTION_API_KEY, page_id=PAGE_ID)
    page, page_results = int_page.get_page()
    assert page
    assert page_results
    page_id_no_dash = page.id.replace("-", "")
    assert PAGE_ID == page_id_no_dash
    # assert page.properties
    blocks = int_page.get_blocks()
    assert blocks
    assert len(blocks) > 0

    child_pages = int_page.get_child_pages()
    assert child_pages
    assert len(child_pages) > 0

    # for child_page in child_pages:
    #     if "test_page" in child_page.title:
    #         print(f"deleting {child_page.title}")
    #         child_page.delete_page()

    test_page = int_page.add_page(title=f"test_page {datetime.now(tz=pytz.utc)}")
    assert test_page

    blocks = []
    blocks.append(NotionBlock.create_table_of_contents_block())
    blocks.append(NotionBlock.create_heading_block("I'm a heading Level 1", level=1))
    blocks.append(NotionBlock.create_paragraph_block("I'm a red bold italic paragraph.", color="red", bold=True, italic=True))
    blocks.append(NotionBlock.create_heading_block("I'm a blue bold italic heading.", level=2, color="blue", bold=True, italic=True))
    blocks.append(NotionBlock.create_heading_block("I'm a heading level 3", level=3))
    blocks.append(NotionBlock.create_heading_block("I'm a heading at default level."))
    blocks.append(NotionBlock.create_heading_block("I'm a heading level 2", level=2))
    blocks.extend(NotionBlock.create_to_do_block(["I'm a to-do list.", "Another Item"], checked=[True, False]))
    blocks.append(NotionBlock.create_heading_block("I'm a heading.", level=2))
    blocks.append(NotionBlock.create_quote_block("I'm a quote."))
    blocks.append(NotionBlock.create_heading_block("I'm a heading.", level=3))
    blocks.append(NotionBlock.create_code_block("import os", language="python"))
    blocks.append(NotionBlock.create_code_block("#include <stdio.h>", language="c"))
    blocks.append(
        NotionBlock.create_embed_block(
            "https://www.notion.so/cosgroma/Planning-for-product-development-cb0163c37cca49848345104644b544d9?pvs=4"
        )
    )
    blocks.append(
        NotionBlock.create_toggle_block("I'm a toggle list.", children=[NotionBlock.create_paragraph_block("I'm a child block.")])
    )
    blocks.append(NotionBlock.create_divider_block())
    blocks.append(NotionBlock.create_link_to_page_block(page_id=PAGE_ID))
    test_page.set_blocks(blocks=blocks)
    list_items = ["List Item 1", "List Item 2"]
    blocks.append(NotionBlock.create_list_block(list_items, True))
    # create_table_block(rows: List[List[str]], headers: Optional[List[str]] = None) -> dict:
    # blocks.append(NotionBlock.create_table_block([["A", "B"], ["1", "2"]], headers=["A", "B"]))
    # create_breadcrumb_block(items: List[Dict[str, str]]) -> dict:
    # blocks.append(NotionBlock.create_breadcrumb_block([{"text": "A", "url": "https://www.notion.so/cosgroma/Planning-for-product-development-cb0163c37cca49848345104644b544d9?pvs=4"}]))
    # create_callout_block(icon: str, text: str) -> dict:
    # blocks.append(NotionBlock.create_callout_block(icon="🚀", text="I'm a callout."))

    # create_column_list_block(columns: List[List[dict]]) -> dict:
    # blocks.append(NotionBlock.create_column_list_block(columns=[[NotionBlock.create_paragraph_block("I'm a column."), NotionBlock.create_paragraph_block("I'm a column.")]]))
    # create_column_block(blocks: List[dict]) -> dict:
    # blocks.append(NotionBlock.create_column_block(blocks=[NotionBlock.create_paragraph_block("I'm a column."), NotionBlock.create_paragraph_block("I'm a column.")]))

    # def get_page(self, force: bool = False) -> Page:
    # def get_blocks(self, force: bool = False) -> List[dict]:
    # def set_blocks(self, blocks: List[dict], clear: bool = False):
    # def clear_blocks(self):
    # def add_page(self, title: str, title_prop: Optional[str] = "Name") -> "NotionPage":
    # def get_child_pages(self, force: bool = False) -> List["NotionPage"]:
    # def delete_child_pages(self):


# def test_notion_page_class():
#     assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
#     assert TEST_PLANNING_PAGE_URL, "TEST_PLANNING_PAGE_URL not set, set it in .env file"
#     int_page = NotionPage(token=NOTION_API_KEY, page_id=PAGE_ID)
#     int_page.save(type="json")
#     # sub_page = int_page.add_page(title=f"test_page {datetime.now(tz=pytz.utc)}")
#     child_pages = int_page.get_child_pages()
#     assert child_pages
#     assert len(child_pages) > 0
#     found_page = False
#     for child_page in child_pages:
#         if "test_page" in child_page.title:
#             found_page = True
#             child_page.delete_page()
#     assert found_page
#     if not found_page:
#         pytest.fail()


class Task(Page):
    name = TitleText("Name")
    tags = MultiSelect("Tags")
    status = Status("Status")
    # assigned_to = Person("Assigned to")
    # date_start = DateRangeStart("Date")
    # date_end = DateRangeEnd("Date")
    # closed_at = Date("Closed at")


# id


class Recording(Page):
    ref = TitleText("Ref")
    file_path = Text("File Path")
    size_bytes = Number("Size Bytes")
    length_seconds = Number("Length Seconds")
    upload_date = Date("Upload Date")
    processed = Checkbox("Processed")

    def __str__(self):
        return f"Recording({self.ref}, {self.file_path}, {self.size_bytes})"


def _test_notion_database_class():
    assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
    assert TEST_PLANNING_PAGE_URL, "TEST_PLANNING_PAGE_URL not set, set it in .env file"
    DB_URL = "https://www.notion.so/cosgroma/62c81d1feaaf485288b4758ec7516b89?v=380a231034534e04b678fd0c80d4ccf9&pvs=4"
    # DB_ID = "62c81d1feaaf485288b4758ec7516b89"
    DB_ID = utils.extract_id_from_notion_url(DB_URL)
    # test_db = NotionDatabase(token=NOTION_API_KEY, database_id=DB_ID, DataClass=Task)

    test_db = NotionDatabase(token=NOTION_API_KEY, database_id=DB_ID, DataClass=Recording)

    RECORDINGS_JSON = "tests\\recordings.json"
    # Read records
    with Path.open(RECORDINGS_JSON, "r") as f:
        recordings = json.load(f)

    # Save records to database
    for recording in recordings:
        recording["ref"] = recording["id"]
        print(recording)
        entry = Recording.new(**recording)
        print(entry)
        # test_db.read(entry)
        test_db.create(obj=entry)
        break
    test_db.load_from_json(RECORDINGS_JSON, DB_ID, Recording)


def test_notion_database_properties():
    assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
    DB_URL = "https://www.notion.so/cosgroma/62c81d1feaaf485288b4758ec7516b89?v=380a231034534e04b678fd0c80d4ccf9&pvs=4"
    # DB_ID = "62c81d1feaaf485288b4758ec7516b89"
    DB_ID = utils.extract_id_from_notion_url(DB_URL)
    test_db = NotionDatabase(token=NOTION_API_KEY, database_id=DB_ID, DataClass=Task)
    properties = test_db.get_properties()
    assert properties
    assert len(properties) > 0

    # save properties to json
    with Path.open("output/test_db_properties.json", "w") as f:
        f.write(json.dumps(properties, indent=4))

    test_db.add_property("New Tags", "multi_select")
    properties = test_db.get_properties()
    found_new_tags = False
    for key in properties.keys():
        prop = properties[key]
        if prop["name"] == "New Tags":
            found_new_tags = True
            assert prop["type"] == "multi_select"
    assert found_new_tags

    test_db.remove_property("New Tags")
    properties = test_db.get_properties()
    found_new_tags = False
    for key in properties.keys():
        prop = properties[key]
        if prop["name"] == "New Tags":
            found_new_tags = True
    assert not found_new_tags

    # title
    # name
    # number
    # formula
    # select
    # multi_select
    # status
    # relation
    # unique_id
    # rich_text
    # url
    # date
    # checkbox
    # button
    # location

    # task = Task.new()
    # task.name = "Take out the trash"
    # task.tags = ["Test", "Tags"]
    # task.status = "In progress"
    # entry = test_db.create(obj=task)
    # print(entry)


# def test_notion_database_clear():
#     assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
#     assert TEST_PLANNING_PAGE_URL, "TEST_PLANNING_PAGE_URL not set, set it in .env file"
#     # int_page = NotionPage(token=NOTION_API_KEY, page_id=PAGE_ID)
#     DB_URL = "https://www.notion.so/cosgroma/62c81d1feaaf485288b4758ec7516b89?v=380a231034534e04b678fd0c80d4ccf9&pvs=4"
#     # DB_ID = "62c81d1feaaf485288b4758ec7516b89"
#     DB_ID = utils.extract_id_from_notion_url(DB_URL)
#     test_db = NotionDatabase(token=NOTION_API_KEY, database_id=DB_ID, DataClass=Task)
#     test_db.delete_all()


# def test_create_paragraph_block():
#     block = NotionBlock.create_paragraph_block("I'm a paragraph.")
#     assert block
#     assert block["paragraph"]
#     assert block["paragraph"]["rich_text"]
#     assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a paragraph."
#     assert block["paragraph"]["color"] == "default"

#     block = NotionBlock.create_paragraph_block("I'm a red paragraph.", color="red")
#     assert block
#     assert block["paragraph"]
#     assert block["paragraph"]["rich_text"]
#     assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a red paragraph."
#     assert block["paragraph"]["color"] == "red"

#     block = NotionBlock.create_paragraph_block(
#         "I'm a link paragraph.",
#         link="https://www.notion.so/cosgroma/Planning-for-product-development-cb0163c37cca49848345104644b544d9?pvs=4",
#     )
#     assert block
#     assert block["paragraph"]
#     assert block["paragraph"]["rich_text"]
#     assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a link paragraph."
#     assert (
#         block["paragraph"]["rich_text"][0]["href"]
#         == "https://www.notion.so/cosgroma/Planning-for-product-development-cb0163c37cca49848345104644b544d9?pvs=4"
#     )

#     block = NotionBlock.create_paragraph_block("I'm a bold paragraph.", bold=True)
#     assert block
#     assert block["paragraph"]
#     assert block["paragraph"]["rich_text"]
#     assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a bold paragraph."
#     assert block["paragraph"]["rich_text"][0]["annotations"]["bold"]

#     block = NotionBlock.create_paragraph_block("I'm an italic paragraph.", italic=True)
#     assert block
#     assert block["paragraph"]
#     assert block["paragraph"]["rich_text"]
#     assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm an italic paragraph."
#     assert block["paragraph"]["rich_text"][0]["annotations"]["italic"]

#     block = NotionBlock.create_paragraph_block("I'm a strikethrough paragraph.", strikethrough=True)
#     assert block
#     assert block["paragraph"]
#     assert block["paragraph"]["rich_text"]
#     assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a strike-through paragraph."


# def test_create_heading_block():
#     block = NotionBlock.create_heading_block("I'm a heading.")
#     assert block
#     assert block["heading_1"]
#     assert block["heading_1"]["text"][0]["plain_text"] == "I'm a heading."

#     block = NotionBlock.create_heading_block("I'm a heading.", level=2)
#     assert block
#     assert block["heading_2"]
#     assert block["heading_2"]["text"][0]["plain_text"] == "I'm a heading."

#     block = NotionBlock.create_heading_block("I'm a heading.", level=3)
#     assert block
#     assert block["heading_3"]
#     assert block["heading_3"]["text"][0]["plain_text"] == "I'm a heading."

#     block = NotionBlock.create_heading_block("I'm expect a value error", level=4)
#     assert not block


def test_create_numbered_list_block(): ...


def test_create_bullet_list_block():
    # blocks.append(NotionBlock.create_list_block(["I'm a bulleted list.", "I'm a bulleted list."], numbered=False))
    ...


def test_create_to_do_block(): ...


def test_create_rich_text(): ...


def test_create_quote_block(): ...


def test_create_code_block(): ...


def test_create_embed_block(): ...


def test_create_toggle_block(): ...


def test_create_divider_block(): ...


def test_create_table_block(): ...


def test_create_breadcrumb_block(): ...


def test_create_callout_block(): ...


def test_create_link_to_page_block(): ...


def test_create_table_of_contents_block(): ...


def test_notion_block():
    # test_create_paragraph_block()
    # test_create_heading_block()
    test_create_to_do_block()
    test_create_rich_text()
    test_create_quote_block()
    test_create_code_block()
    test_create_embed_block()
    test_create_toggle_block()
    test_create_divider_block()
    test_create_table_block()
    test_create_breadcrumb_block()
    test_create_callout_block()
    test_create_link_to_page_block()
    test_create_table_of_contents_block()


if __name__ == "__main__":
    # test_client()
    # test_exporter_export_url()
    # test_exporter_export_page()
    # test_exporter_export_database()
    test_notion_page()
    print("databasetools tests passed")
