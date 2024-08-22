from __future__ import annotations

import os
from builtins import Exception
from pathlib import Path
from typing import Annotated
from typing import Generator

import frontmatter
from bson import ObjectId

from ...models.docblock import DocBlockElement
from ...models.docblock import DocBlockElementType
from ...models.docblock import PageElement
from ...models.docblock import PageTypes
from ...utils.docBlock.docBlock_utils import ToDocBlock
from ...utils.log import logger
from ..confluence.cf_adapter import cf_pre_process


class OneNote_2_MongoBlocks:
    """Attaches to a directory on the local drive and provides two generators to make MongoBlocks.

    To use:
        1. Init OneNote_2_MongoBlocks
        2. Call get_export_page and upload to mongo collection.
        3. Use "folder_page_gen" to generate all folder blocks and upload to the same mongo collection.
        4. Use "file_page_gen" to generate all file blocks and upload the PageElements to the export mongo collection and the DocBlocks to a DocBlock collection. Use the resource list to upload files to a gridFS instance.

    The first generator is "folder_page_gen" which generates PageElements representing the folder structure in the export directory.
    The second generator is "file_page_gen" which generates a PageElement representing the markdown file, a list of DocBlockElements that make up the content of the page, and lastly, a list of paths pointing to required resources.
    """

    def __init__(self, dir_path: str | Path) -> None:
        self.root_path: Annotated[Path, 'Path to the root directory which holds the "resources" and the notebook folders.'] = Path(dir_path)
        self.export_id: Annotated[ObjectId, "Id of the export which is created when this class is instantiated."] = ObjectId()
        self._check_dir()
        self._resource_path: Annotated[Path, "Path to the resource folder of the export."] = self.root_path / "resources"
        self._export_path: Annotated[
            Path, 'Path to the notebook folder which should be the other folder besides "resources" in "self.root_path"'
        ] = self.root_path / next(
            iter([file for file in os.listdir(self.root_path) if file != "resources"])
        )  # This ain't sketchy at all :D

        self._md_file_list: Annotated[
            dict[Path, ObjectId],
            "Is a dictionary of the paths to each markdown file in the notebook export and the id the page element should have representing the markdown file.",
        ]
        self._folder_list: Annotated[
            dict[Path, ObjectId],
            "Is a dictionary of the paths to each folder in the notebook export and the id the page element should have representing the folder",
        ]
        self._missed_files: Annotated[list[Path], "A list of paths corresponding to files that OneNote_2_MongoBlocks could not deal with."]
        self._md_file_list, self._folder_list, self._missed_files = self._find_files(self._export_path)

    def get_export_page(self) -> PageElement:
        """Returns an "export" type PageElement corresponding to the export instance created by this class instance.

        Raises:
            KeyError: If somehow the _folder_list was initiated improperly and the export has no id.

        Returns:
            PageElement: A PageElement object with type: PageTypes.EXPORT and with with the child being the root folder of the export.
        """
        root_page_id = self._folder_list.get(self._export_path)
        if root_page_id is None:
            # I can see this happening but don't know how it can happen.
            raise KeyError(
                "If you are seeing this, a One Note export was started but somehow, OneNote_2_MongoBlocks did not catch the export notebook name. This should not be possible?"
            )
        return PageElement(
            type=PageTypes.EXPORT,
            id=self.export_id,
            children=[root_page_id],
            export_name=self._export_path.name.rstrip(),
        )

    def _check_dir(self) -> None:
        """Checks a directory to make sure it is in the correct export format. A correctly formatted oneNote export from onenote-exporter should have two folders in the export directory: "resources" and another folder with the name of the export.

        Raises:
            NotOneNoteExport: If the directory is not a onenote export.
            FileExistsError: Found two folders but can't find a "resources" folder.
        """
        items = list(os.listdir(self.root_path))
        if len(items) not in [1, 2]:
            raise NotOneNoteExport(
                f"Directory {self.root_path} is not in the correct format. One note exports should only have two folders. Files found: {items}"
            )
        elif len(items) == 2:
            if "resources" not in items:
                raise FileExistsError(f"Two folders found but one of them is not a resource folder. Items found {items}")

    def _find_files(self, dir_path: Path) -> tuple[dict[Path, ObjectId], dict[Path, ObjectId], list[Path]]:
        """Returns two dictionaries relating paths to files in a OneNote export to objectid's which should be the id's of the PageElements generated later. The last item is a list of paths which are not parsed.

        Args:
            dir_path (Path): Path of a directory which folders and files will be tabulated.

        Returns:
            tuple[dict[Path, ObjectId], dict[Path, ObjectId], list[Path]]: First item correlates files with id's, the second item correlates folders with id's and last item lists missed files.
        """
        files = {}
        folders = {dir_path: ObjectId()}
        not_md_files = []
        for item in os.listdir(dir_path):
            item_path = dir_path / item
            logger.info(f"Collecting: {item_path}")
            if item_path.is_dir():
                sub_files, sub_folders, sub_not_md = self._find_files(item_path)
                files = {**files, **sub_files}
                folders = {**folders, **sub_folders}
                not_md_files.extend(sub_not_md)
            elif item_path.suffix == ".md":
                files = {**files, item_path: ObjectId()}
            else:
                not_md_files.append(item_path)
        return files, folders, not_md_files

    def folder_page_len(self):
        return len(self._folder_list)

    def folder_page_gen(self) -> Generator[PageElement, None, None]:
        """Generates PageElements according to the folder list. Folder PageElements relate to each other through the "sub_folders" attribute. The "children" attribute is reserved to id's to "page" type PageElements.

        Yields:
            Generator[PageElement, None, None]: Generates PageElements one-by-one to not overload memory in case of extremely large exports.
        """
        for folder in self._folder_list:
            children_folders = []
            children_files = []
            for file in os.listdir(folder):
                file_path = folder / file
                if file_path.is_dir():
                    children_folders.append(file_path)
                else:
                    children_files.append(file_path)
            yield PageElement(
                id=self._folder_list[folder],
                type=PageTypes.FOLDER,
                name=folder.name.rstrip(),
                sub_folders=[self._folder_list[folder_path] for folder_path in children_folders],
                children=[self._md_file_list[file_path] for file_path in children_files],
                export_name=self._export_path.name.rstrip(),
                export_id=self.export_id,
                relative_path=os.path.relpath(folder, self._export_path),  # relative path compared to the root export directory
            )

    def file_page_len(self):
        return len(self._md_file_list)

    def file_page_gen(self) -> Generator[tuple[PageElement, list[DocBlockElement], list[Path]], None, None]:
        """Generates page MongoBlocks one-by-one according to _md_file_list.

        Yields:
            Generator[tuple[PageElement, list[DocBlockElement], list[Path]], None, None]: The first element returned in the tuple is the page element corresponding to the PageElement representing the markdown file. The second element is a list of DocBlockElements which make up the content of the markdown file. The last element is a list of paths which correspond to the resources that are required to build the page.
        """
        for file in self._md_file_list:

            with file.open("r") as md_file:
                metadata, raw_md = frontmatter.parse(md_file.read())

            formatted_md = cf_pre_process(raw_md)
            title = str(file.stem) if metadata.get("title") is None else str(metadata.get("title"))
            block_list, id_list = ToDocBlock.parse_md2docblock(formatted_md, mode=ToDocBlock.ONE_NOTE_MODE)

            new_page_element = PageElement(
                type=PageTypes.PAGE,
                id=self._md_file_list[file],
                children=id_list,
                name=title.rstrip(),
                created_at=metadata["created"],
                modified_at=metadata["updated"],
                export_name=self._export_path.name.rstrip(),
                export_id=self.export_id,
                relative_path=os.path.relpath(file, self._export_path),
            )

            for block in block_list:
                block.export_id = self.export_id

            required_resources = self._check_resources(block_list)

            yield new_page_element, block_list, required_resources

    def _check_resources(self, block_list: list[DocBlockElement]) -> list[Path]:
        """Checks if all resources referenced by a list of DocBlockElements exists in a folder.

        Args:
            block_list (list[DocBlockElement]): A list of DocBlockElements to check.

        Raises:
            FileExistsError: If the resource file DNE
            NameError: If the reference has a bad name.

        Returns:
            list[Path]: A list of Paths that make sense.
        """
        required_resources = []
        for block in block_list:
            if block.type == DocBlockElementType.RESOURCE_REFERENCE:
                basename = block.block_attr.get("basename")
                if basename is not None:
                    resource_path: Path = self._resource_path / basename
                    if resource_path.exists():
                        required_resources.append(resource_path)
                    else:
                        raise FileExistsError(f"Resource reference file: {resource_path} does not exist.")
                else:
                    raise NameError(f"Resource reference has no basename: {block}")
        return required_resources


class NotOneNoteExport(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
