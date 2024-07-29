import os
from builtins import Exception
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

import frontmatter
from bson import ObjectId

from databasetools.managers.docs_manager import DocManager
from databasetools.models.docblock import DocBlockElement
from databasetools.models.docblock import DocBlockElementType
from databasetools.utils.docBlock.docBlock_utils import ToDocBlock


class OneNoteTools:
    def __init__(
        self, db_uri: str, docblock_db_name: Optional[str] = None, grid_db_name: Optional[str] = None, col_name: Optional[str] = None
    ):
        collection_info = None if col_name is None else (col_name, DocBlockElement)
        self._manager = DocManager(
            mongo_uri=db_uri, doc_block_db_name=docblock_db_name, gridFS_db_names=grid_db_name, docblock_col_infos=collection_info
        )
        self._resource_name = grid_db_name if grid_db_name is not None else DocManager.RESOURCES
        self._col_name = col_name if col_name is not None else DocManager.DOC_BLOCKS

        self.__current_dir_name = None
        self.__current_dir_path = None
        self.__current_export_id = None

    @property
    def _current_dir_name(self):
        return self.__current_dir_name

    @property
    def _current_dir_path(self):
        return self.__current_dir_path

    @property
    def _current_export_id(self):
        return self.__current_export_id

    @_current_dir_path.setter
    def _current_dir_path(self, dir_path: Union[Path, str]):
        if self._current_dir_path:
            raise AlreadyAttachedToDir(f"Already working on a directory: {self.__current_dir_path}")
        else:
            self.__current_dir_path = Path(dir_path)
            self.__current_dir_name = self.__current_dir_path.name
            self.__current_export_id = ObjectId()

    @_current_dir_path.deleter
    def _current_dir_path(self):
        self.__current_dir_path = None
        self.__current_dir_name = None
        self.__current_export_id = None

    def upload_oneNote_export(self, dir_path: Union[Path, str]) -> List[Union[Path, str]]:
        """Tailored to upload oneNote exports which should contain a "resources" folder and another folder containing the markdown content. Uploads both the resources and Markdown as DocBlockElements into the MongoDB instance.

        Args:
            dir_path (Union[Path, str]): Path to the oneNote export directory.

        Raises:
            NotOneNoteExport: Directory at "dir_path" contains other than 1 or 2 folders.
            FileExistsError: Directory at "dir_path" has 2 folders but one of them is not a "resources" folder.

        Returns:
            List[Union[Path, str]]: A list of paths specifying the files that were not parsed and uploaded to Mongo.
        """
        items = list(os.listdir(dir_path))

        # A oneNote export may have 2 formats:
        # 1. 2 folders, a "resources" folder and a folder with the markdown exports named as the notebook that was exported.
        # 2. 1 folder with the name of the exported notebook (no resources)
        if len(items) not in [1, 2]:
            raise NotOneNoteExport(
                f"Directory {dir_path} is not in the correct format. One note exports should only have two folders. Files found: {items}"
            )
        elif len(items) == 2:
            if "resources" not in items:
                raise FileExistsError(f"Two folders found but one of them is not a resource folder. Items found {items}")

        for item in items:
            dir_path = Path(dir_path)
            if item == "resources":
                self.store_resources(dir_path / "resources")
            else:
                raw_path = dir_path / item
                self._current_dir_path = raw_path
                missed_files = self.upload_md_dir(raw_path)
                del self._current_dir_path
        return missed_files

    def upload_md_dir(self, dir_path: Union[Path, str], depth: int = -1) -> List[Union[Path, str]]:
        """Recursively uploads files to a MongoDB instance in a directory up to a folder depth. If the depth starts negative, will process all the files contained in the directory tree.

        Args:
            dir_path (Union[Path, str]): Path to the directory.
            depth (int, optional): Max nest depth to reach into the directory. Defaults to -1.

        Raises:
            FileNotFoundError: Specified file does not exist.
            NotADirectoryError: Specified file is not a directory.

        Returns:
            List[Union[Path, str]]: A list of paths specifying the files that were not parsed and uploaded into the MongoDB instance.
        """
        if depth == 0:
            return

        dir_path = Path(dir_path)
        missed_files = []

        if not dir_path.exists():
            raise FileNotFoundError(f"The specified filepath: {dir_path} does not exist.")
        elif not dir_path.is_dir():
            raise NotADirectoryError(f"File path provided is not a directory: {dir_path}")

        for item in os.listdir(dir_path):
            item_path = dir_path / item

            if item_path.is_dir():
                missed_files.extend(self.upload_md_dir(item_path, depth - 1))
                continue

            try:
                block_list = self._parse_page_from_file(item_path)
                self._upload_block_list(block_list)
            except NotMDFileError:
                missed_files.append(item_path)
            except Exception as e:
                raise Exception(f"From file {item_path}") from e

        return missed_files

    def _upload_block_list(self, block_list: List[DocBlockElement]):
        """Uploads a list of DocBlockElements.

        Args:
            block_list (List[DocBlockElement]): List of elements to upload to the Mongo instance attached to this class.
        """
        for item in block_list:
            self._manager.upload_to_col(self._col_name, item)

    def _parse_page_from_file(self, file_path: Union[Path, str]) -> List[DocBlockElement]:
        """Parses a Markdown file into a list of DocBlockElements with the first element of the list being the page block.

        Args:
            file_path (Union[Path, str]): Path to the Markdown file.

        Raises:
            TypeError: Raised when the input file is to a directory.
            FileExistsError: Path points to a file that does not exist.
            NotMDFileError: Extension of the file is not ".md"

        Returns:
            List[DocBlockElement]: A list of DocBlockElements of the parsed Markdown file.
        """
        file_path = Path(file_path)

        if file_path.is_dir():
            raise TypeError(f"Path: {file_path}, points to a directory.")
        elif not file_path.exists():
            raise FileExistsError(f"File: {file_path}, does not exist!")
        elif not file_path.name.endswith(".md"):
            raise NotMDFileError(f"File: {file_path}, does not end with .md!")

        with file_path.open("r") as md_file:
            metadata, md = frontmatter.parse(md_file.read())

        block_list, id_list = ToDocBlock.parse_md2docblock(md, mode=ToDocBlock.ONE_NOTE_MODE)

        relative_path = None

        if self._current_dir_path:
            relative_path = os.path.relpath(file_path, self._current_dir_path)

        new_attrs = {
            "oneNote_created_at": metadata.get("created"),
            "oneNote_modified_at": metadata.get("updated"),
            "oneNote_path": metadata.get("oneNotePath"),
            "export_name": self._current_dir_name,
            "export_relative_path": relative_path,
        }

        new_block = DocBlockElement(
            type=DocBlockElementType.PAGE,
            children=id_list,
            name=str(metadata.get("title")),
            block_attr=new_attrs,
            export_id=self._current_export_id,
        )

        block_list.insert(0, new_block)
        return block_list

    def store_resources(self, dir_path: Union[Path, str]):
        """Given a directory, uploads the contents into a GridFS instance on the MongoDB attached to this class.

        Args:
            dir_path (Union[Path, str]): Path to the resources directory.

        Raises:
            FileNotFoundError: "dir_path" DNE
        """
        dir_path = Path(dir_path)

        if not dir_path.is_dir():
            raise FileNotFoundError(f"The specified directory path: {dir_path} does not exist.")

        for item in os.listdir(dir_path):
            item_path = dir_path / item
            item_name = item_path.stem
            extension = item_path.suffix

            with item_path.open("rb") as f:
                self._manager.upload_to_grid(self._resource_name, f.read(), filename=item_name, extension=extension)

    def verify_references(self):
        missing_resource = []
        items = self._manager.find_in_col(self._col_name, type="resource_reference")
        for item in items:
            filename = item.block_attr["filename"]
            extension = item.block_attr["extension"]
            result = self._manager.find_in_grid(self._resource_name, filename=filename, extension=extension)
            if result:
                item.status = "Verified"
            else:
                missing_resource.append(item)
        return missing_resource

    def get_resource(self, file_name: str, extension: str):
        grid_out = self._manager.find_in_grid(self._resource_name, filename=file_name, extension=extension)
        return grid_out.read()


class NotOneNoteExport(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AlreadyAttachedToDir(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotMDFileError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
