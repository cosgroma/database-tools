# exporter = NotionExporter(token=token)
# path = exporter.export_url(url=url)
# print(f" * Exported to {path}")

import os

from databasetools import notion_exporter

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
PAGE_URL = os.getenv("PAGE_URL")
TEST_DATABASE_ID = os.getenv("TEST_DATABASE_ID")
PAGE_ID = os.getenv("PAGE_ID")


def test_exporter():
    exporter = notion_exporter.NotionExporter(token=NOTION_API_KEY)
    path = exporter.export_url(url=PAGE_URL)
    assert path.exists()
    path = exporter.export_database(database_id=TEST_DATABASE_ID)
    assert path.exists()
    path = exporter.export_page(page_id=PAGE_ID)
    assert path.exists()


def test_recent_pages():
    exporter = notion_exporter.NotionExporter(token=NOTION_API_KEY)
    pages = exporter.downloader.get_recent_pages()
    assert len(pages) > 0


if __name__ == "__main__":
    test_recent_pages()
    print(" * All tests passed!")
