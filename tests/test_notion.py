# exporter = NotionExporter(token=token)
# path = exporter.export_url(url=url)
# print(f" * Exported to {path}")

from databasetools import notion_exporter

NOTION_API_KEY = "secret_9TbvSMWaQM1lMEGX743sm8qOFx9GBLeflfKHgi7S1IP"
TEST_DATABASE_ID = "62c81d1feaaf485288b4758ec7516b89"
PAGE_URL = "https://www.notion.so/cosgroma/Integration-Test-Area-44a057c1ee38483b8d88c9a5e6d3dce2?pvs=4"
DATABASE_URL = "https://www.notion.so/cosgroma/62c81d1feaaf485288b4758ec7516b89?v=380a231034534e04b678fd0c80d4ccf9&pvs=4"
PAGE_ID = "44a057c1ee38483b8d88c9a5e6d3dce2"


def test_exporter():
    exporter = notion_exporter.NotionExporter(token=NOTION_API_KEY)
    path = exporter.export_url(url=PAGE_URL)
    assert path.exists()
    path = exporter.export_database(database_id=TEST_DATABASE_ID)
    assert path.exists()
    path = exporter.export_page(page_id=PAGE_ID)
    assert path.exists()
