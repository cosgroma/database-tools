from typing import ClassVar
from typing import List
from typing import Optional

from gridfs import GridFS
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from ..controller.mongo_controller import MongoCollectionController
from ..models.block_model import DocBlockElement

DEFAULT_MANAGER = "default_manager"
ONE_NOTE_MANAGER = "one_note_manager"


class DocManager:
    _instances: ClassVar = {}

    def __init__(
        self,
        mongo_uri: Optional[str] = None,
        docblock_db_name: Optional[str] = None,
        gridFS_db_name: Optional[str] = None,
        docblock_col_name: Optional[str] = None,
    ):

        self._mongo_uri: str = mongo_uri
        self._docblock_db_name: str = docblock_db_name
        self._gridFS_db_name: str = gridFS_db_name
        self._docblock_col_name: str = docblock_col_name

        self._mongo_client: MongoClient = None
        self._gridFS_db: Database = None
        self._docblock_db: Database = None
        self._gridFS_client: GridFS = None
        self._docblock_col: Collection = None
        self._docblock_col_controller: MongoCollectionController = None

        self.connect_all()

    @staticmethod
    def get_instance(
        instance_name: str = DEFAULT_MANAGER,
        mongo_uri: Optional[str] = None,
        docblock_db_name: Optional[str] = None,
        gridFS_db_name: Optional[str] = None,
        docblock_col_name: Optional[str] = None,
    ):
        if not DocManager._instances.get(instance_name):
            DocManager._instances[instance_name] = DocManager(mongo_uri, docblock_db_name, gridFS_db_name, docblock_col_name)
        return DocManager._instances[instance_name]

    def connect_all(self):
        self._complete = (
            self._mongo_uri is not None
            and self._docblock_db_name is not None
            and self._gridFS_db_name is not None
            and self._docblock_col_name is not None
        )
        if self._complete:
            self._mongo_client = MongoClient(self._mongo_uri)
            self._gridFS_db = self._mongo_client[self._gridFS_db_name]
            self._docblock_db = self._mongo_client[self._docblock_db_name]
            self._gridFS_client = GridFS(self._gridFS_db)
            self._docblock_col = self._docblock_db[self._docblock_col_name]
            self._docblock_col_controller = MongoCollectionController(self._docblock_col, DocBlockElement)
        self._connected = (
            self._mongo_client is not None
            and self._gridFS_db is not None
            and self._docblock_db is not None
            and self._gridFS_client is not None
            and self._docblock_col is not None
            and self._docblock_col_controller is not None
        )

    def close_all(self):
        self._gridFS_db = None
        self._docblock_db = None
        self._gridFS_client = None
        self._docblock_col = None
        self._docblock_col_controller = None
        self._mongo_client.close()
        self._mongo_client = None
        self._connected = False

    @property
    def mongo_uri(self):
        return self._mongo_uri

    @property
    def docblock_db_name(self):
        return self._docblock_db_name

    @property
    def gridFS_db_name(self):
        return self._gridFS_db_name

    @property
    def docblock_col_name(self):
        return self._docblock_col_name

    @mongo_uri.setter
    def mongo_uri(self, new_mongo_uri: str):
        if new_mongo_uri != self._mongo_uri:
            self.close_all()
            self._mongo_uri = new_mongo_uri
            self.connect_all()

    @docblock_db_name.setter
    def docblock_db_name(self, new_db_name: str):
        if new_db_name != self.docblock_db_name:
            self.close_all()
            self.docblock_db_name = new_db_name
            self.connect_all()

    @gridFS_db_name.setter
    def gridFS_db_name(self, new_db_name: str):
        if new_db_name != self.gridFS_db_name:
            self.close_all()
            self.gridFS_db_name = new_db_name
            self.connect_all()

    @docblock_col_name.setter
    def docblock_col_name(self, new_col_name: str):
        if new_col_name != self.docblock_col_name:
            self.close_all()
            self.docblock_col_name = new_col_name
            self.connect_all()

    def check_connection(func):
        def with_check(self, *args):
            if not self._connected:
                return False
            else:
                return func(self, *args)

        return with_check

    def fs_store_file(self, data: bytes, **kwargs):
        return self._gridFS_client.put(data, **kwargs)

    def fs_find_file(self, **kwargs):
        return self._gridFS_client.find_one(dict(kwargs))

    @check_connection
    def reset_resources(self):
        self._mongo_client.drop_database(self._gridFS_db_name)
        self.gridFS_db_name = self.gridFS_db_name

    @check_connection
    def reset_collection(self):  # Danger zone! For testing only!
        self._docblock_col_controller.delete_all()

    def upload_block(self, block: DocBlockElement):
        try:
            return self._docblock_col_controller.create(block)
        except Exception as e:
            raise Exception(f"Trying to add block: {block}") from e

    def update_block(self, block: DocBlockElement):
        return self._docblock_col_controller.update({"element_id": block.id}, block)

    def sync_block(self, block: DocBlockElement):
        update_result = self.update_block(block)
        if update_result:
            return block
        return self.upload_block(block)

    def find_blocks(self, **kwargs) -> List[DocBlockElement]:
        return self._docblock_col_controller.read(dict(kwargs))


class IncompleteClassError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
