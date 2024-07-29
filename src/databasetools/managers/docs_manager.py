from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from gridfs import GridFS
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from databasetools.controller.base_controller import T

from ..controller.mongo_controller import MongoCollectionController
from ..models.docblock import DocBlockElement

DATABASE = 0
GRID_CLIENT = 1
COLLECTION = 0
COL_CON = 1


class DocManager:
    # Default, always initiated, gridFS name
    RESOURCES = "resources"
    # Default, always initiated, collection name
    DOC_BLOCKS = "doc_blocks"

    def __init__(
        self,
        mongo_uri: Optional[str] = None,
        doc_block_db_name: Optional[str] = None,
        gridFS_db_names: Optional[Union[List[str], str]] = None,
        docblock_col_infos: Optional[Union[List[Tuple[str, T]], Tuple[str, T]]] = None,
    ) -> None:
        gridFS_db_names = (
            [gridFS_db_names] if isinstance(gridFS_db_names, str) else gridFS_db_names
        )  # Allows users to input just one string or a list of strings
        docblock_col_infos = [docblock_col_infos] if isinstance(docblock_col_infos, Tuple) else docblock_col_infos

        if gridFS_db_names is None:
            gridFS_db_names = [DocManager.RESOURCES]
        elif DocManager.RESOURCES not in gridFS_db_names:
            gridFS_db_names.append(DocManager.RESOURCES)

        if docblock_col_infos is None:
            docblock_col_infos = [(DocManager.DOC_BLOCKS, DocBlockElement)]
        elif (DocManager.DOC_BLOCKS, DocBlockElement) not in docblock_col_infos:
            docblock_col_infos.append((DocManager.DOC_BLOCKS, DocBlockElement))

        self._mongo_uri: str = mongo_uri
        self._grid_names: List[str] = gridFS_db_names
        self._col_infos: List[Tuple[str, T]] = docblock_col_infos
        self._db_db_name = "DocBlocks" if doc_block_db_name is None else doc_block_db_name  # "Doc Block DataBase name" ;)

        self._mongo_client: MongoClient = MongoClient(self._mongo_uri)
        self._docblock_db: Database = self._mongo_client[self._db_db_name]
        self._grids: Dict[str, Tuple[Database, GridFS]] = self.make_grids(self._grid_names)
        self._collections: Dict[str, Tuple[Collection, MongoCollectionController]] = self.make_collections(self._col_infos)

    def get_collection(self, name: str) -> Tuple[Collection, MongoCollectionController]:
        return self._collections[name]

    def get_grid(self, name: str) -> Tuple[Database, GridFS]:
        return self._grids[name]

    def make_grids(self, names: Union[str, List[str]]) -> Dict[str, Tuple[Database, GridFS]]:
        names = [names] if isinstance(names, str) else names
        new_grids = {}
        for name in names:
            db_instance = self._mongo_client[name]
            grid_client = GridFS(db_instance)
            new_grids[name] = (db_instance, grid_client)
        return new_grids

    def make_collections(self, names: Union[Tuple[str, T], List[Tuple[str, T]]]) -> Dict[str, Tuple[Collection, MongoCollectionController]]:
        names = [names] if isinstance(names, Tuple) else names
        new_cols = {}
        for name, block_type in names:
            collection_instance = self._docblock_db[name]
            collection_controller = MongoCollectionController(collection_instance, block_type)
            new_cols[name] = (collection_instance, collection_controller)
        return new_cols

    def reset_collections(self, names: Optional[Union[str, List[str]]] = None) -> None:
        """Resets collections specified by "names" by deleting all documents in those collections. If no name is specified, this method will delete all documents in all collections in the doc_block database.

        Args:
            names (Optional[Union[str, List[str]]], optional): Names of the collections to reset. If None, this method will delete ALL documents in ALL collections under the doc_block database. Defaults to None.
        """
        names = [names] if isinstance(names, str) else names
        if names is None:
            names = [name for name, _ in self._col_infos]

        for name in names:
            self._collections[name][COL_CON].delete_all()

    def reset_grids(self, names: Optional[Union[str, List[str]]] = None) -> None:
        """Resets grid instances by dropping the associated database and re-instantiating each instance. If no gridDB name is given, ALL gridDB instances will be reset.

        Args:
            names (Optional[Union[str, List[str]]], optional): Names of the gridDB's to reset. If None, this method will reset ALL gridDBs. Defaults to None.
        """
        names = [names] if isinstance(names, str) else names
        if names is None:
            names = self._grid_names

        for name in names:
            self._mongo_client.drop_database(name)
            self._grids[name] = self.make_grids(name)[name]

    def upload_to_col(self, collection_name: str, block: T):
        controller = self._collections[collection_name][COL_CON]
        try:
            return controller.create(block)
        except Exception as e:
            raise Exception(f"Whilst uploading block: {block} to {collection_name}") from e

    def find_in_col(self, collection_name: str, **kwargs) -> List[DocBlockElement]:
        controller = self._collections[collection_name][COL_CON]
        return controller.read(dict(kwargs))

    def upload_to_grid(self, grid_name: str, data: bytes, **kwargs):
        grid_dude = self._grids[grid_name][GRID_CLIENT]
        try:
            return grid_dude.put(data, **kwargs)
        except Exception as e:
            raise Exception(f"While attempting to upload data to grid instance: {grid_name}, with arguments: {kwargs}") from e

    def find_in_grid(self, grid_name: str, **kwargs):
        grid_dude = self._grids[grid_name][GRID_CLIENT]
        return grid_dude.find_one(dict(kwargs))
