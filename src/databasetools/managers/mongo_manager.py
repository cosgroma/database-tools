import logging
import os
import re
import tempfile
import urllib.parse
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from atlassian.errors import ApiError
from bson import ObjectId
from gridfs import GridFS
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from ..adapters.confluence.cf_adapter import cf_post_process
from ..adapters.confluence.confluence import ConfluenceManager
from ..adapters.oneNote.oneNote import OneNote_2_MongoBlocks
from ..controller.base_controller import T
from ..controller.mongo_controller import MongoCollectionController
from ..models.docblock import DocBlockElement
from ..models.docblock import PageElement
from ..models.docblock import PageTypes
from ..utils.docBlock.docBlock_utils import FromDocBlock
from ..utils.log import logger

"""
    Usage:
    1. Instantiate MongoManager.
    2. Call MongoManager.upload_one_note() with a valid directory path to a onenote export by onenote-exporter and store the output which is an export id for the upload to mongo.
    3. Call MongoManager.upload_confluence() with a valid export id and the page id of a page on confluence (where the export would be uploaded under)
    4. Wait...

    Notes:
    1. You must let upload_one_note to complete without errors once completely to not have any missing data in the mongodb.
    2. You may stop upload_confluence while running since it can detect when a page is already on confluence and which ones need to be uploaded.
    3. If you need to reupload a page on confluence, right now you just go in manually and set "confluence_space_name" to null. This will prompt upload_confluence to restart the upload for that page next time it is run with the page's export id.
"""


class MongoManager:
    """IMPORTANT: Exports using the onenote-exporter MUST have "DeduplicateLinebreaks" and "MaxTwoLineBreaksInARow", set to false."""

    # Default, always initiated, gridFS name
    RESOURCES = "resources"
    # Default, always initiated, collection name for storing docBlocks
    DOC_BLOCKS = "doc_blocks"
    # Default, always initiated, collection name to store confluence data
    PAGE_DATA = "page_data"

    def __init__(
        self,
        mongo_uri: str,
        confluence_url: str,
        confluence_space_key: str,
        confluence_user_name: str,
        confluence_api_token: str,
        doc_block_db_name: Optional[str] = None,
        gridFS_db_names: Optional[Union[List[str], str]] = None,
        col_infos: Optional[Union[List[Tuple[str, T]], Tuple[str, T]]] = None,
    ) -> None:
        self.confluence_url = confluence_url
        self.confluence_space_key = confluence_space_key
        self.confluence_user_name = confluence_user_name
        self.confluence_api_token = confluence_api_token
        self.con_ad = ConfluenceManager(confluence_url, confluence_space_key, confluence_user_name, confluence_api_token)

        if gridFS_db_names is None:
            gridFS_db_names = []

        if col_infos is None:
            col_infos = []

        if isinstance(gridFS_db_names, str):  # Store the init name to assign as active grid later
            init_grid_name = gridFS_db_names
        else:
            init_grid_name = None

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

        if init_grid_name:
            self.active_grid = init_grid_name

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
        controller = self._collections[collection_name][1]  # collection client is teh second element of the collections tuple
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
        controller = self._collections[collection_name][1]  # collection controller is the second element of the collections tuple
        return controller.read(dict(kwargs))

    def find_one_in_col(self, collection_name: str, **kwargs) -> T:
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

    def del_many_in_col(self, collection_name: str, **kwargs):
        controller = self._collections[collection_name][1]  # Collection controller is second element of collections tuple
        return controller.delete(dict(kwargs))

    def del_in_grid(self, grid_name: str, **kwargs):
        grid_dude = self._grids[grid_name][1]
        grid_collection = self._grids[grid_name][0].get_collection("fs.files")
        docs = grid_collection.find(dict(kwargs))
        id_list = [doc["_id"] for doc in docs]
        for id in id_list:
            grid_dude.delete(id)

    # One Note export upload things
    def upload_one_note_2_mongo(self, dir_path: Union[Path, str]) -> ObjectId:
        on = OneNote_2_MongoBlocks(dir_path)
        export_page = on.get_export_page()
        export_id = on.export_id
        logger.info(f"Beginning export: {export_page.name}")

        try:  # To catch any error during upload to mongo. If there are errors, you might not have a complete upload to mongo but there is no way to "pick up" from where we left off so we delete all progress before we exit.
            self.upload_to_col(self.active_page_col, export_page)
            self._upload_OneNote_folder_struct(on)
            self._upload_OneNote_files(on)
            return export_page.id
        except BaseException as e:  # If there is any error during the upload, we should drop all progress we have made so far.
            self._clean_incomplete_mongo_upload(export_id)
            raise IncompleteUpload(
                "Failed to completely upload all data from export to mongo. Deleting partial upload to prevent corruption."
            ) from e

    def _upload_OneNote_folder_struct(self, ON_adapter: OneNote_2_MongoBlocks) -> None:
        for folder_page in ON_adapter.folder_page_gen():
            logger.info(f"Uploading info page for: {folder_page.relative_path}")
            self.upload_to_col(self.active_page_col, folder_page)

    def _upload_OneNote_files(self, ON_adapter: OneNote_2_MongoBlocks) -> None:
        for page, block_list, required_resources_list in ON_adapter.file_page_gen():  # Upload page pages to mongo
            logger.info(f"Uploading page: {page.relative_path}")
            for block in block_list:
                self.upload_to_col(self.active_db_col, block)

            for resource in required_resources_list:  # Upload resources for each page to gridFS
                logger.info(f"\tUploading resource {resource.name}")
                with resource.open("rb") as file:
                    self.upload_to_grid(
                        self.active_grid, file.read(), name=resource.name, confluence_id=None, export_id=ON_adapter.export_id
                    )

            self.upload_to_col(self.active_page_col, page)

    def _clean_incomplete_mongo_upload(self, export_id: ObjectId):
        logger.info("Begin cleaning export from Mongo")
        self.del_many_in_col(self.active_db_col, export_id=export_id)
        self.del_many_in_col(self.active_page_col, export_id=export_id)
        self.del_in_grid(self.active_grid, export_id=export_id)
        logger.info("Finished cleaning mongo")
        logger.critical("Failed to finish upload to mongo!")

    # Confluence Upload things
    def upload_confluence(self, export_id: ObjectId, parent_id: Optional[str] = None, parent_title: Optional[str] = None) -> bool:
        if parent_id is None:  # Establish "root" page on confluence
            if parent_title:
                parent_id = self.con_ad.get_confluence_page_id(parent_title)
                if not parent_id:
                    result_page = self.con_ad.make_confluence_page_directory(parent_title)
                    parent_id = result_page["id"]

        export_page_element: PageElement = self.find_one_in_col(self.active_page_col, id=export_id, type=PageTypes.EXPORT)
        root_page_element: PageElement = self.find_one_in_col(self.active_page_col, id=export_page_element.children[0])

        if export_page_element is None:  # Just in case the export page does not exist in the case that the export_id is invalid
            raise KeyError(f"Invalid Export id: {export_id}")

        self._make_page_tree(root_page_element, parent_id)  # Makes a page tree on confluence

        folder_page_elements: List[PageElement] = self.find_in_col(
            self.active_page_col, type=PageTypes.FOLDER
        )  # Finds all folders then determines if its child pages need to be made on confluence

        logger.info("Begin uploading files to confluence:")
        for folder_element in folder_page_elements:  # For each page in each folder...
            if not folder_element.children:
                continue

            for page_id in folder_element.children:
                try:
                    file_block: PageElement = self.find_one_in_col(self.active_page_col, id=page_id)
                except Exception as e:
                    raise Exception(f"While trying to find block with id: {page_id} in collection: {self.active_page_col}") from e

                complete_upload = (  # Goofy linter made it multiline
                    True
                    if file_block.confluence_page_id is not None
                    and file_block.confluence_page_name is not None
                    and file_block.confluence_space_key is not None
                    else False
                )

                if not complete_upload:
                    if file_block.confluence_page_id:
                        try:
                            page = self.con_ad.confluence_client.get_page_by_id(file_block.confluence_page_id)
                            self.con_ad.delete_page(file_block.confluence_page_id)
                            logger.info(f"Restarting page upload for: {page['title']}")
                        except ApiError:
                            file_block.confluence_page_name = None
                            file_block.confluence_space_key = None
                        file_block.confluence_page_id = None

                    try:
                        logger.info(f"Reconstructing page {file_block.name}")
                        updated_block = self._construct_page(file_block, folder_element.confluence_page_id)
                    except IncompleteUpload as e:
                        if len(e.args) == 2:
                            file_block.confluence_page_id = e.args[1]
                            self.update_to_col(self.active_page_col, file_block, id=file_block.id)
                        else:
                            raise e

                    self.update_to_col(self.active_page_col, updated_block, id=updated_block.id)

    def _construct_page(self, file_block: PageElement, parent_id: str) -> PageElement:
        block_list = self._get_block_tree(file_block.children)

        content, required_resources = FromDocBlock.render_docBlock(block_list, file_block.children)

        try:  # Make an empty page
            new_page = self.con_ad.make_confluence_page(file_block.name, "Under construction...", parent_id)
            new_page_name = new_page["title"]
            new_page_id = new_page["id"]
        except Exception as e:
            raise IncompleteUpload(
                f"Exception occurred while uploading page with file block: \n{file_block}\n\nWith content: \n{content}"
            ) from e

        try:  # Upload attachments
            self._add_attachment(required_resources, new_page_id)
        except Exception as e:
            raise IncompleteUpload(f"Exception occurred during upload of page {new_page_id}", new_page_id) from e

        # Do final content formatting
        content = self.format_final_html(content, new_page_name, new_page_id)

        try:  # Update the empty page with the formatted content
            self.con_ad.update_confluence_page(new_page_id, new_page_name, content)
        except Exception as e:
            raise IncompleteUpload(f"Exception occurred while trying to update page {new_page_id}", new_page_id) from e

        # Update blocks to contain the correct info
        file_block.confluence_page_id = new_page_id
        file_block.confluence_page_name = new_page_name
        file_block.confluence_space_key = new_page["space"]["key"]

        return file_block

    def format_final_html(self, html_from_docblock: str, page_name: str, page_id: str) -> str:
        content = cf_post_process(html_from_docblock)  # POTENTIAL FOR CATASTROPHIC BACKTRACKING: WATCH FOR CONTINUOUS PRINTOUTS.

        # Find the rest of the attachment links and parse them to a coherent format that confluence can use
        # This is the url extension to preview an attachment
        # /display/{space_key}/{page_name}?preview=/{confluence_page_id}/{attachment_id}
        MISC_ATTACHMENT_PATTERN = re.compile(r"""<a\s+href="(\w+?\.\w+?)">(.*?)</a>""")

        def repl(m: re.Match):
            attachment_grid_item = self.find_in_grid(self.active_grid, name=m.group(1))
            attachment_confluence_id = attachment_grid_item.__getattr__("confluence_id")
            if self.confluence_url.endswith("/"):
                con_url = self.confluence_url
            else:
                con_url = self.confluence_url + "/"

            esc_con_space_key = urllib.parse.quote_plus(self.confluence_space_key)
            esc_page_name = urllib.parse.quote_plus(page_name)

            return f"""<a href="{con_url}display/{esc_con_space_key}/{esc_page_name}?preview=/{page_id}/{attachment_confluence_id}">{m.group(2)}</a>"""

        return re.sub(MISC_ATTACHMENT_PATTERN, repl, content)

    def _add_attachment(self, resources: List[str], page_id_to_add_attachments: str):
        temp_dir = Path(tempfile.mkdtemp())

        def remove_dir():
            for item in os.listdir(temp_dir):
                (temp_dir / item).unlink()
            temp_dir.rmdir()

        try:
            for resource in resources:
                logger.info(f"Uploading {resource}")
                try:
                    grid_out = self.find_in_grid(self.active_grid, name=resource)
                except Exception as e:
                    remove_dir()
                    raise Exception(f"Exception occurred while finding: {resource}, in gridFS instance: {self.active_grid}") from e

                if grid_out is None:
                    remove_dir()
                    raise FileNotFoundError(f"Can't find resource: {resource}'")

                temp_file = temp_dir / resource
                try:
                    with temp_file.open("wb") as file:
                        file.write(grid_out.read())
                except Exception as e:
                    remove_dir()
                    raise Exception(
                        f"Exception occurred while attempting to read: {resource}, from gridFS instance {self.active_grid}"
                    ) from e

                try:
                    response = self.con_ad.add_confluence_attachments(temp_file, page_id_to_add_attachments)
                    fs_file_col = self._grids[self.active_grid][0].get_collection("fs.files")
                    if (result := response.get("results")) is not None:
                        if result[0].get("type") == "attachment":
                            attachment_id = result[0]["id"]
                        else:
                            raise KeyError(f"Unexpected response object: {response}")
                    else:
                        if response.get("type") == "attachment":
                            attachment_id = response["id"]
                        else:
                            raise KeyError(f"Unexpected response object: {response}")

                    fs_file_col.update_one(filter={"name": resource}, update={"$set": {"confluence_id": attachment_id}})
                    temp_file.unlink()
                except Exception as e:
                    raise Exception(
                        f"Exception occurred while attempting to upload, {resource} to gridFS instance {self.active_grid}"
                    ) from e
        finally:
            remove_dir()

    def _make_page_tree(self, folder_block: PageElement, parent_id: str):
        if not folder_block.confluence_page_id:
            new_page = self.con_ad.make_confluence_page_directory(folder_block.name, parent_id)
            folder_block.confluence_page_id = new_page["id"]
            folder_block.confluence_page_name = new_page["title"]
            folder_block.confluence_space_key = new_page["space"]["key"]

        self.update_to_col(self._active_page_col, folder_block, id=folder_block.id)
        for child_id in folder_block.sub_folders:
            child_block = self.find_one_in_col(self.active_page_col, id=child_id)
            self._make_page_tree(child_block, folder_block.confluence_page_id)

    def _get_block_tree(self, block_ids: List[DocBlockElement]) -> List[DocBlockElement]:
        block_list = []

        for block_id in block_ids:
            this_block: DocBlockElement = self.find_one_in_col(self.active_db_col, id=block_id)
            block_list.extend(self._get_block_tree(this_block.children))
            block_list.append(this_block)

        return block_list

    # Debug a page. Prints out a page tree.
    def print_debug_tree(self, page_element_id: Union[ObjectId, str]):
        if isinstance(page_element_id, str):
            page_element_id = ObjectId(page_element_id)

        page_element: PageElement = self.find_one_in_col(self.active_page_col, id=page_element_id)
        if not isinstance(page_element, PageElement):
            raise KeyError(f"Id provided to print correlates to an object that is not a page element! id: {page_element_id}")

        def make_children_list(block_dict: Dict[ObjectId, DocBlockElement], block: DocBlockElement) -> List[str]:
            if block.block_content is not None:
                print_list = [f"Block Element id: {block.id!s}\tType: {block.type}\tRaw: {block.block_content}"]
            else:
                print_list = [f"Block Element id: {block.id!s}\tType: {block.type}"]
            for cblock_id in block.children:
                c_list = make_children_list(block_dict, block_dict[cblock_id])
                for i in range(len(c_list)):
                    c_list[i] = f"\t{c_list[i]}"
                print_list.extend(c_list)
            return print_list

        print_list = [f"\nPage Element id: {page_element.id}\tName: {page_element.name}\tExport id: {page_element.export_id}"]
        block_list = self._get_block_tree(page_element.children)
        block_dict = {block.id: block for block in block_list}
        for block_id in page_element.children:
            new_list = make_children_list(block_dict, block_dict[block_id])
            print_list.extend(new_list)

        for item in print_list:
            logging.debug(item)


class IncompleteUpload(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
