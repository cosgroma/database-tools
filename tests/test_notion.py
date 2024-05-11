# exporter = NotionExporter(token=token)
# path = exporter.export_url(url=url)
# print(f" * Exported to {path}")

import os
import shutil
from datetime import datetime
from pathlib import Path

import pytz

import databasetools.block as NotionBlock
from databasetools import NotionClient
from databasetools import NotionExporter
from databasetools import NotionPage

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
PAGE_URL = os.getenv("PAGE_URL")
TEST_DATABASE_ID = os.getenv("TEST_DATABASE_ID")
PAGE_ID = os.getenv("PAGE_ID")


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


exporter = NotionExporter(token=NOTION_API_KEY)


def test_exporter_export_url():
    # Make test directory
    assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
    assert PAGE_URL, "PAGE_URL not set, set it in .env file"
    assert TEST_DATABASE_ID, "TEST_DATABASE_ID not set, set it in .env file"

    test_page_name = "test_page_url"
    json_dir = f"{test_page_name}/json"
    md_dir = f"{test_page_name}/md"
    json_path = Path(json_dir)
    md_path = exporter.export_url(url=PAGE_URL, json_dir=json_dir, md_dir=md_dir)
    assert md_path.exists()
    assert md_path.is_file()
    assert md_path.suffix == ".md"

    # assert len(os.listdir(md_path)) > 0
    assert json_path.exists()
    assert json_path.is_dir()
    shutil.rmtree(test_page_name)


def test_exporter_export_page():
    test_page_name = "test_page"
    json_dir = f"{test_page_name}/json"
    md_dir = f"{test_page_name}/md"
    md_path = exporter.export_page(page_id=PAGE_ID, json_dir=json_dir, md_dir=md_dir)
    json_path = Path(json_dir)
    assert md_path.is_file()
    assert md_path.suffix == ".md"
    assert json_path.exists()
    assert json_path.is_dir()
    shutil.rmtree(test_page_name)


def test_exporter_export_database():
    # exporter = NotionExporter(token=NOTION_API_KEY)
    test_db_name = "test_db"
    json_dir = f"{test_db_name}/json"
    md_dir = f"{test_db_name}/md"
    md_path = exporter.export_database(database_id=TEST_DATABASE_ID, json_dir=json_dir, md_dir=md_dir)
    json_path = Path(json_dir)
    assert md_path.is_dir()
    assert len(os.listdir(md_path)) > 0
    assert json_path.exists()
    assert len(os.listdir(json_dir)) > 0
    shutil.rmtree(test_db_name)


TEST_PLANNING_PAGE_URL = "https://www.notion.so/cosgroma/Planning-for-product-development-cb0163c37cca49848345104644b544d9?pvs=4"

# class Page(NotionObject):
#     id: str = Id()
#     created_time: datetime = RootProperty()
#     last_edited_time: datetime = RootProperty()


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

    for child_page in child_pages:
        if "test_page" in child_page.title:
            print(f"deleting {child_page.title}")
            child_page.delete_page()
        if "Planning" in child_page.title:
            planning_page = "planning_page"
            json_dir = f"{planning_page}/json"
            md_dir = f"{planning_page}/md"
            md_path = exporter.export_page(page_id=child_page.page_id, json_dir=json_dir, md_dir=md_dir)
            json_path = Path(json_dir)
            assert md_path.is_file()
            assert md_path.suffix == ".md"
            assert json_path.exists()
            assert json_path.is_dir()

    test_page = int_page.add_page(title=f"test_page {datetime.now(tz=pytz.utc)}")
    assert test_page

    blocks = []
    blocks.append(NotionBlock.create_table_of_contents_block())
    blocks.append(NotionBlock.create_heading_block("I'm a heading.", level=1))
    blocks.append(NotionBlock.create_paragraph_block("I'm a red bold italic paragraph.", color="red", bold=True, italic=True))
    blocks.append(NotionBlock.create_heading_block("I'm a blue bold italic heading.", level=2, color="blue", bold=True, italic=True))
    blocks.append(NotionBlock.create_list_block(["I'm a bulleted list.", "I'm a bulleted list."], numbered=False))
    blocks.append(NotionBlock.create_heading_block("I'm a heading.", level=3))
    blocks.append(NotionBlock.create_list_block(["I'm a numbered list.", "I'm a numbered list."], numbered=True))
    blocks.append(NotionBlock.create_heading_block("I'm a heading."))
    blocks.append(NotionBlock.create_heading_block("I'm a heading.", level=2))
    blocks.append(NotionBlock.create_to_do_block("I'm a to-do list.", checked=True))
    blocks.append(NotionBlock.create_heading_block("I'm a heading.", level=2))
    blocks.append(NotionBlock.create_to_do_block("I'm a to-do list.", checked=False))
    blocks.append(NotionBlock.create_quote_block("I'm a quote."))
    blocks.append(NotionBlock.create_heading_block("I'm a heading.", level=2))
    blocks.append(NotionBlock.create_code_block("import os", language="python"))
    blocks.append(NotionBlock.create_code_block("#include <stdio.h>", language="c"))
    # create_embed_block(url: str) -> dict:
    blocks.append(
        NotionBlock.create_embed_block(
            "https://www.notion.so/cosgroma/Planning-for-product-development-cb0163c37cca49848345104644b544d9?pvs=4"
        )
    )
    # create_toggle_block(text: str, children: List[dict] = None) -> dict:
    blocks.append(
        NotionBlock.create_toggle_block("I'm a toggle list.", children=[NotionBlock.create_paragraph_block("I'm a child block.")])
    )
    # create_divider_block() -> dict:
    blocks.append(NotionBlock.create_divider_block())
    blocks.append(NotionBlock.create_link_to_page_block(page_id=PAGE_ID))

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

    test_page.set_blocks(blocks=blocks)
    # def get_page(self, force: bool = False) -> Page:
    # def get_blocks(self, force: bool = False) -> List[dict]:
    # def set_blocks(self, blocks: List[dict], clear: bool = False):
    # def clear_blocks(self):
    # def add_page(self, title: str, title_prop: Optional[str] = "Name") -> "NotionPage":
    # def get_child_pages(self, force: bool = False) -> List["NotionPage"]:
    # def delete_child_pages(self):


def test_create_paragraph_block():
    block = NotionBlock.create_paragraph_block("I'm a paragraph.")
    assert block
    assert block["paragraph"]
    assert block["paragraph"]["rich_text"]
    assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a paragraph."
    assert block["paragraph"]["color"] == "default"

    block = NotionBlock.create_paragraph_block("I'm a red paragraph.", color="red")
    assert block
    assert block["paragraph"]
    assert block["paragraph"]["rich_text"]
    assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a red paragraph."
    assert block["paragraph"]["color"] == "red"

    block = NotionBlock.create_paragraph_block(
        "I'm a link paragraph.",
        link="https://www.notion.so/cosgroma/Planning-for-product-development-cb0163c37cca49848345104644b544d9?pvs=4",
    )
    assert block
    assert block["paragraph"]
    assert block["paragraph"]["rich_text"]
    assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a link paragraph."
    assert (
        block["paragraph"]["rich_text"][0]["href"]
        == "https://www.notion.so/cosgroma/Planning-for-product-development-cb0163c37cca49848345104644b544d9?pvs=4"
    )

    block = NotionBlock.create_paragraph_block("I'm a bold paragraph.", bold=True)
    assert block
    assert block["paragraph"]
    assert block["paragraph"]["rich_text"]
    assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a bold paragraph."
    assert block["paragraph"]["rich_text"][0]["annotations"]["bold"]

    block = NotionBlock.create_paragraph_block("I'm an italic paragraph.", italic=True)
    assert block
    assert block["paragraph"]
    assert block["paragraph"]["rich_text"]
    assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm an italic paragraph."
    assert block["paragraph"]["rich_text"][0]["annotations"]["italic"]

    block = NotionBlock.create_paragraph_block("I'm a strikethrough paragraph.", strikethrough=True)
    assert block
    assert block["paragraph"]
    assert block["paragraph"]["rich_text"]
    assert block["paragraph"]["rich_text"][0]["plain_text"] == "I'm a strike-through paragraph."


def test_create_heading_block():
    block = NotionBlock.create_heading_block("I'm a heading.")
    assert block
    assert block["heading_1"]
    assert block["heading_1"]["text"][0]["plain_text"] == "I'm a heading."

    block = NotionBlock.create_heading_block("I'm a heading.", level=2)
    assert block
    assert block["heading_2"]
    assert block["heading_2"]["text"][0]["plain_text"] == "I'm a heading."

    block = NotionBlock.create_heading_block("I'm a heading.", level=3)
    assert block
    assert block["heading_3"]
    assert block["heading_3"]["text"][0]["plain_text"] == "I'm a heading."

    block = NotionBlock.create_heading_block("I'm expect a value error", level=4)
    assert not block


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
    test_create_paragraph_block()
    test_create_heading_block()
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
