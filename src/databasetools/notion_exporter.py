from pathlib import Path
from typing import Optional
from typing import Union

from .json2md import JsonToMdConverter
from .notion import NotionDownloader


class NotionExporter:
    def __init__(self, token: str, strip_meta_chars: Optional[str] = None, extension: str = "md", filter: Optional[dict] = None):
        self.downloader = NotionDownloader(token, filter)
        self.converter = JsonToMdConverter(strip_meta_chars=strip_meta_chars, extension=extension)

    def export_url(self, url: str, json_dir: Union[str, Path] = "./json", md_dir: Union[str, Path] = "./md") -> Path:
        """Export the notion page or database."""
        self.downloader.download_url(url, json_dir)
        return self.converter.convert(json_dir, md_dir)

    def export_database(self, database_id: str, json_dir: Union[str, Path] = "./json", md_dir: Union[str, Path] = "./md") -> Path:
        """Export the notion database and associated pages."""
        self.downloader.download_database(database_id, json_dir)
        return self.converter.convert(json_dir, md_dir)

    def export_page(self, page_id: str, json_dir: Union[str, Path] = "./json", md_dir: Union[str, Path] = "./md"):
        """Export the notion page."""
        json_dir_path = Path(json_dir)
        self.downloader.download_page(page_id, json_dir_path / f"{page_id}.json")
        return self.converter.convert(json_dir, md_dir)
