# exporter = NotionExporter(token=token)
# path = exporter.export_url(url=url)
# print(f" * Exported to {path}")

import os
import shutil
from pathlib import Path

from databasetools import NotionClient
from databasetools import NotionExporter

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


def test_exporter_export_url():
    # Make test directory
    assert NOTION_API_KEY, "NOTION_API_KEY not set, set it in .env file"
    assert PAGE_URL, "PAGE_URL not set, set it in .env file"
    assert TEST_DATABASE_ID, "TEST_DATABASE_ID not set, set it in .env file"

    exporter = NotionExporter(token=NOTION_API_KEY)
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
    exporter = NotionExporter(token=NOTION_API_KEY)
    # os.makedirs("test_page", exist_ok=True)
    test_page_name = "test_page"
    json_dir = f"{test_page_name}/json"
    md_dir = f"{test_page_name}/md"
    md_path = exporter.export_page(page_id=PAGE_ID, json_dir=json_dir, md_dir=md_dir)
    json_path = Path(json_dir)
    assert md_path.is_file()
    assert md_path.suffix == ".md"
    assert json_path.exists()
    assert json_path.is_dir()
    # shutil.rmtree(test_page_name)


def test_exporter_export_database():
    exporter = NotionExporter(token=NOTION_API_KEY)
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
