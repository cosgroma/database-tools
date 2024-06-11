import os
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from notion_objects import Page

from ..adapters.notion import NotionClient
from ..adapters.notion import NotionDatabase
from .base_controller import DatabaseController
from .base_controller import T

NOTION_API_KEY = os.getenv("NOTION_API_KEY")


class NotionDatabaseController(DatabaseController[T]):
    def __init__(self, token: str, database_id: Optional[str] = None, DataClass: Optional[Type[T]] = None):
        super().__init__()
        self.token = token
        self.n_client = NotionClient(token=token)
        self.database_id = database_id
        self.DataClass = DataClass or Page  # Default to Page if no DataClass provided
        self._db = NotionDatabase(token=NOTION_API_KEY, database_id=self.database_id, DataClass=self.DataClass)

    def create(self, data: Dict[str, Any]) -> T:
        # Implementation specific to Notion
        entry = self.DataClass.new(**data)
        return self._db.create(obj=entry)

    def read(self, query: Dict[str, Any]) -> List[T]:
        # Implementation specific to Notion
        return self._db.read(query["id"])

    def update(self, obj: Type[T], update_data: Dict[str, Any]) -> bool:
        # Implementation specific to Notion
        return self._db.update(obj, properties=update_data)

    def delete(self, obj: Type[T]) -> bool:
        # Implementation specific to Notion
        self._db.delete(obj)

    def __iter__(self) -> List[T]:
        # Specific to Notion
        return iter(self._db.get_pages())

    def __repr__(self):
        return f"NotionDatabaseController(db_id={self.database_id})"
