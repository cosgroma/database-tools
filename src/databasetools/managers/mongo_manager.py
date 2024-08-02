import os
import tempfile
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from bson import ObjectId
from gridfs import GridFS
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from ..adapters.confluence.cf_adapter import image2cf
from ..adapters.confluence.confluence import ConfluenceManager
from ..adapters.oneNote.oneNote import OneNoteTools
from ..controller.base_controller import T
from ..controller.mongo_controller import MongoCollectionController
from ..models.docblock import DocBlockElement
from ..models.docblock import PageElement
from ..models.docblock import PageTypes
from ..utils.docBlock.docBlock_utils import FromDocBlock


class MongoManager:
    # Default, always initiated, gridFS name
    RESOURCES = "resources"
    # Default, always initiated, collection name for storing docBlocks
    DOC_BLOCKS = "doc_blocks"
    # Default, always initiated, collection name to store confluence data
    PAGE_DATA = "page_data"

    def __init__(
        self,
        mongo_uri: Optional[str] = None,
        doc_block_db_name: Optional[str] = None,
        gridFS_db_names: Optional[Union[List[str], str]] = None,
        col_infos: Optional[Union[List[Tuple[str, T]], Tuple[str, T]]] = None,
    ) -> None:
        if gridFS_db_names is None:
            gridFS_db_names = []

        if col_infos is None:
            col_infos = []

        gridFS_db_names = [gridFS_db_names] if isinstance(gridFS_db_names, str) else gridFS_db_names
        col_infos = [col_infos] if isinstance(col_infos, tuple) else col_infos

        # Set instance variables: _mongo_uri, _grid_names, _col_infos, _db_db_name
        self._mongo_uri: str = mongo_uri
        self._db_db_name = "DocBlocks" if doc_block_db_name is None else doc_block_db_name  # "Doc Block DataBase name" ;)

        # Mongo Manipulating objects
        self._mongo_client: MongoClient = MongoClient(self._mongo_uri)
        self._db_db: Database = self._mongo_client[self._db_db_name]  # 'DocBlock DataBase' ;)

        # These dictionaries map a grid database name or a collection name to their corresponding manipulating objects.
        # These two lines only inits the collections and databases that are provided during the init of this class.
        # At the end of this init method, we will init the default grid, docblock collection, and page collections.
        self._grids: Dict[str, Tuple[Database, GridFS]] = self.make_grids(gridFS_db_names)
        self._collections: Dict[str, Tuple[Collection, MongoCollectionController]] = self.make_collections(col_infos)

        # Used to reference the "active" collections and grid databases.
        self._active_grid = None
        self._active_db_col = None
        self._active_page_col = None

        # Will init default grids and collections. Also inits the active variables for easier referencing
        self.set_default_actives()

    # Init and class management methods
    @property
    def active_grid(self) -> str:
        return self._active_grid

    @property
    def active_db_col(self) -> str:
        return self._active_db_col

    @property
    def active_page_col(self) -> str:
        return self._active_page_col

    @active_grid.setter
    def active_grid(self, name: str) -> None:
        """Sets the active grid instance with the name of the database with the grid client.

        Args:
            name (str): gird name
        """
        if name not in self._grids:
            new_grid = self.make_grids([name])
            self._grids = {**self._grids, **new_grid}
        self._active_grid = name

    @active_db_col.setter
    def active_db_col(self, db_col_info: Tuple[str, T]) -> None:
        """Sets the active docblock (db) collection (col) with a tuple of the collection info consisting of the name of the collection and the model type it stores.

        Args:
            db_col_info (Tuple[str, T]): docblock collection info. First item is the name of the collection and the second item is the model type it stores.
        """
        self.__set_active_collection_logic(*db_col_info)
        self._active_db_col, _ = db_col_info

    @active_page_col.setter
    def active_page_col(self, page_col_info: Tuple[str, T]) -> None:
        """Sets the active page collection (col) with the collection info.

        Args:
            page_col_info (Tuple[str, T]): First item should be the collection name. The second item should be the model type that is stored in the collection.
        """
        self.__set_active_collection_logic(*page_col_info)
        self._active_page_col, _ = page_col_info

    def set_default_actives(self) -> None:
        """Resets the collections and grids back to default."""
        self.active_grid = MongoManager.RESOURCES
        self.active_db_col = MongoManager.DOC_BLOCKS, DocBlockElement
        self.active_page_col = MongoManager.PAGE_DATA, PageElement

    def __set_active_collection_logic(self, name: str, model: Optional[T] = None) -> None:
        """Helper function. Sets the instance variables that represent the active collections.

        Args:
            name (str): Name of the collection.
            model (Optional[T], optional): Model that the collection stores. Defaults to None.

        Raises:
            KeyError: If a name is provided but no model is provided AND the collection does not already exist.
        """
        if name not in self._collections:
            if model is not None:
                new_collections = self.make_collections([(name, model)])
                self._collections = {**self._collections, **new_collections}
            else:
                raise KeyError(
                    f"If the collection does not exist, you must also provide the model type so MongoManager can instantiate the collection. Error making collection {name} with no model given"
                )

    def get_collection(self, name: str) -> Tuple[Collection, MongoCollectionController]:
        """Returns the collection object and the controller object associated with a collection name.

        Args:
            name (str): Name of the collection in self._collections.

        Returns:
            Tuple[Collection, MongoCollectionController]: First object is the collection object from MongoClient. Second object is the controller object for this collection.
        """
        return self._collections[name]

    def get_grid(self, name: str) -> Tuple[Database, GridFS]:
        """Returns the database object and the gridFS client associated with a gridFS name.

        Args:
            name (str): Name of the gridFS database.

        Returns:
            Tuple[Database, GridFS]: First object is the database object the second is the gridFS client.
        """
        return self._grids[name]

    def make_collections(self, collection_infos: List[Tuple[str, T]]) -> Dict[str, Tuple[Collection, MongoCollectionController]]:
        """Makes a new collection under the database stored under the instance's db_db

        Args:
            collection_infos (List[Tuple[str, T]]): List of collection infos which are tuples of collection names and the models that the respective collection stores.

        Returns:
            Dict[str, Tuple[Collection, MongoCollectionController]]: A dictionary correlating the collection name with the connection objects.
        """
        new_cols = {}
        for name, block_type in collection_infos:
            collection_instance = self._db_db[name]
            collection_controller = MongoCollectionController(collection_instance, block_type)
            new_cols[name] = (collection_instance, collection_controller)
        return new_cols

    def make_grids(self, names: List[str]) -> Dict[str, Tuple[Database, GridFS]]:
        """Makes new grid objects and returns a dictionary of the grid name and the grid objects.

        Args:
            names (List[str]): A list of grid names that should be created

        Returns:
            Dict[str, Tuple[Database, GridFS]]: A dictionary correlating the grid names with the connection objects
        """
        new_grids = {}
        for name in names:
            db_instance = self._mongo_client[name]
            grid_client = GridFS(db_instance)
            new_grids[name] = (db_instance, grid_client)
        return new_grids

    # Actual mongo manipulating methods
    def reset_collections(self, names: Optional[Union[str, List[str]]] = None) -> None:
        """Resets collections specified by "names" by deleting all documents in those collections. If no name is specified, this method will delete all documents in all collections in the doc_block database.

        Args:
            names (Optional[Union[str, List[str]]], optional): Names of the collections to reset. If None, this method will delete ALL documents in ALL collections under the doc_block database. Defaults to None.
        """
        names = list(names) if isinstance(names, str) else names
        if names is None:
            names = list(self._collections)

        for name in names:
            self._collections[name][1].delete_all()

    def reset_grids(self, names: Optional[Union[str, List[str]]] = None) -> None:
        """Resets grid instances by dropping the associated database and re-instantiating each instance. If no gridDB name is given, ALL gridDB instances will be reset.

        Args:
            names (Optional[Union[str, List[str]]], optional): Names of the gridDB's to reset. If None, this method will reset ALL gridDBs. Defaults to None.
        """
        names = list(names) if isinstance(names, str) else names
        if names is None:
            names = list(self._grids)

        for name in names:
            self._mongo_client.drop_database(name)
            self._grids.pop(name)

        reloaded_grids = self.make_grids(names)
        self._grids = {**self._grids, **reloaded_grids}

    def upload_to_col(self, collection_name: str, block: T):
        controller = self._collections[collection_name][1]  # 1 is the collection client
        try:
            return controller.create(block)
        except Exception as e:
            raise Exception(f"Whilst uploading block: {block} to {collection_name}") from e

    def update_to_col(self, collection_name: str, block: T, **query):
        controller = self._collections[collection_name][1]
        try:
            return controller.update(query, block)
        except Exception as e:
            raise Exception(f"While trying to update block {block} to {collection_name}") from e

    def find_in_col(self, collection_name: str, **kwargs) -> List[T]:
        controller = self._collections[collection_name][1]  # 1 is the collection client
        return controller.read(dict(kwargs))

    def find_one_in_col(self, collection_name: str, **kwargs) -> List[T]:
        return self.find_in_col(collection_name, **kwargs)[0]

    def upload_to_grid(self, grid_name: str, data: bytes, **kwargs):
        grid_dude = self._grids[grid_name][1]  # 1 is the grid client
        try:
            return grid_dude.put(data, **kwargs)
        except Exception as e:
            raise Exception(f"While attempting to upload data to grid instance: {grid_name}, with arguments: {kwargs}") from e

    def find_in_grid(self, grid_name: str, **kwargs):
        grid_dude = self._grids[grid_name][1]  # 1 is the grid client
        return grid_dude.find_one(dict(kwargs))

    # One Note export upload things
    def upload_one_note(self, dir_path: Union[Path, str]) -> ObjectId:
        on = OneNoteTools(dir_path)
        export_page = on.get_export_page()
        print(f"Beginning export: {export_page.name}")
        self.upload_to_col(self.active_page_col, export_page)

        for folder_page in on.folder_page_gen():
            print(f"Uploading info page for: {folder_page.relative_path!s}")
            self.upload_to_col(self.active_page_col, folder_page)

        for page, block_list, required_resources_list in on.file_page_gen():
            print(f"Uploading page: {page.relative_path}")
            for block in block_list:
                self.upload_to_col(self.active_db_col, block)

            for resource in required_resources_list:
                print(f"\tUploading resource {resource.name}")
                with resource.open("rb") as file:
                    self.upload_to_grid(self.active_grid, file.read(), name=resource.name)

            self.upload_to_col(self.active_page_col, page)

        return export_page.id

    def upload_confluence(self, export_id: ObjectId, parent_id: Optional[str] = None, parent_title: Optional[str] = None) -> bool:
        CONFLUENCE_UNAME = os.getenv("CONFLUENCE_UNAME")
        CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
        CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")
        CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_API_KEY")
        con_ad = ConfluenceManager(CONFLUENCE_URL, CONFLUENCE_SPACE_KEY, CONFLUENCE_UNAME, CONFLUENCE_TOKEN)

        if parent_id is None:
            if parent_title:
                parent_id = con_ad.get_confluence_page_id(parent_title)
                if not parent_id:
                    result_page = con_ad.make_confluence_page_directory(parent_title)
                    parent_id = result_page["id"]

        export_page_element: PageElement = self.find_one_in_col(self.active_page_col, id=export_id, type=PageTypes.EXPORT)
        root_page_element: PageElement = self.find_one_in_col(self.active_page_col, id=export_page_element.children[0])

        if export_page_element is None:
            raise KeyError(f"Invalid Export id: {export_id}")

        self._make_page_tree(con_ad, root_page_element, parent_id)

        folder_page_elements: List[PageElement] = self.find_in_col(self.active_page_col, type=PageTypes.FOLDER)
        print("Begin files to confluence:")
        for folder_element in folder_page_elements:
            if not folder_element.children:
                continue

            for page_id in folder_element.children:
                file_block: PageElement = self.find_one_in_col(self.active_page_col, id=page_id)
                if not file_block.confluence_page_id:
                    updated_block = self._construct_page(con_ad, file_block, folder_element.confluence_page_id)
                    if not self.update_to_col(self.active_page_col, updated_block, id=updated_block.id):
                        raise RuntimeError(f"Failed to update block: {updated_block}")
                else:
                    continue

    def _construct_page(self, con_ad: ConfluenceManager, file_block: PageElement, parent_id: str) -> PageElement:
        block_list = self._get_block_tree(file_block.children)

        content, required_resources = FromDocBlock.render_docBlock(block_list, file_block.children)
        print(content)
        content = image2cf(content)

        new_page = con_ad.make_confluence_page(file_block.name, content, parent_id)

        self._add_attachment(con_ad, required_resources, new_page["id"])

        file_block.confluence_page_id = new_page["id"]
        file_block.confluence_page_name = new_page["title"]
        file_block.confluence_space_key = new_page["space"]["key"]

        return file_block

    def _add_attachment(self, con_ad: ConfluenceManager, resources: List[str], page_id_to_add_attachments: str):
        temp_dir = Path(tempfile.mkdtemp())
        for resource in resources:
            grid_out = self.find_in_grid(self.active_grid, name=resource)
            if grid_out is None:
                raise FileNotFoundError(f"Can't find resource: {resource}'")

            temp_file = temp_dir / resource
            with temp_file.open("wb") as file:
                file.write(grid_out.read())

        con_ad.add_confluence_attachments(temp_dir, page_id_to_add_attachments)

        for item in os.listdir(temp_dir):
            (temp_dir / item).unlink()
        temp_dir.rmdir()

    def _make_page_tree(self, con_ad: ConfluenceManager, folder_block: PageElement, parent_id: str):
        if not folder_block.confluence_page_id:
            new_page = con_ad.make_confluence_page_directory(folder_block.name, parent_id)
            folder_block.confluence_page_id = new_page["id"]
            folder_block.confluence_page_name = new_page["title"]
            folder_block.confluence_space_key = new_page["space"]["key"]

        self.update_to_col(self._active_page_col, folder_block, id=folder_block.id)
        for child_id in folder_block.sub_folders:
            child_block = self.find_one_in_col(self.active_page_col, id=child_id)
            self._make_page_tree(con_ad, child_block, folder_block.confluence_page_id)

    def _get_block_tree(self, block_ids: List[DocBlockElement]) -> List[DocBlockElement]:
        block_list = []

        for block_id in block_ids:
            this_block: DocBlockElement = self.find_one_in_col(self.active_db_col, id=block_id)
            block_list.extend(self._get_block_tree(this_block.children))
            block_list.append(this_block)

        return block_list
