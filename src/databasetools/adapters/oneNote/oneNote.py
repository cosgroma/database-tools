import os
from builtins import Exception
from pathlib import Path
from typing import Dict
from typing import Generator
from typing import List
from typing import Tuple
from typing import Union

import frontmatter
from bson import ObjectId

from ...models.docblock import DocBlockElement
from ...models.docblock import DocBlockElementType
from ...models.docblock import PageElement
from ...models.docblock import PageTypes
from ...utils.docBlock.docBlock_utils import ToDocBlock
from ..confluence.cf_adapter import space_out_tables


class OneNoteTools:
    def __init__(self, dir_path: Union[str, Path]):
        self.root_path = Path(dir_path)
        self.export_id = ObjectId()
        self._check_dir()
        self._resource_path = self.root_path / "resources"
        self._export_path = self.root_path / next(
            iter([file for file in os.listdir(self.root_path) if file != "resources"])
        )  # This ain't sketchy at all :D
        self._md_file_list, self._folder_list, self._missed_files = self._find_files(self._export_path)

    def get_export_page(self) -> PageElement:
        root_page_id = self._folder_list.get(self._export_path)
        if root_page_id is None:
            # I can see this happening but don't know how it can happen.
            raise KeyError(
                "If you are seeing this, a One Note export was started but somehow, OneNoteTools did not catch the export notebook name. This should not be possible?"
            )
        return PageElement(
            type=PageTypes.EXPORT,
            id=self.export_id,
            children=[root_page_id],
            export_name=self._export_path.name,
        )

    def _check_dir(self) -> None:
        items = list(os.listdir(self.root_path))
        if len(items) not in [1, 2]:
            raise NotOneNoteExport(
                f"Directory {self.root_path} is not in the correct format. One note exports should only have two folders. Files found: {items}"
            )
        elif len(items) == 2:
            if "resources" not in items:
                raise FileExistsError(f"Two folders found but one of them is not a resource folder. Items found {items}")

    def _find_files(self, dir_path: Path) -> Tuple[Dict[Path, ObjectId], Dict[Path, ObjectId], List[Path]]:
        files = {}
        folders = {dir_path: ObjectId()}
        not_md_files = []
        for item in os.listdir(dir_path):
            item_path = dir_path / item
            print(f"Collecting: {item_path}")
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
                name=folder.name,
                sub_folders=[self._folder_list[folder_path] for folder_path in children_folders],
                children=[self._md_file_list[file_path] for file_path in children_files],
                export_name=self._export_path.name,
                export_id=self.export_id,
                relative_path=os.path.relpath(folder, self._export_path),
            )

    def file_page_len(self):
        return len(self._md_file_list)

    def file_page_gen(self) -> Generator[Tuple[PageElement, List[DocBlockElement], List[Path]], None, None]:
        for file in self._md_file_list:

            with file.open("r") as md_file:
                metadata, raw_md = frontmatter.parse(md_file.read())

            formatted_md = space_out_tables(raw_md)
            title = str(file.stem) if metadata.get("title") is None else str(metadata.get("title"))
            block_list, id_list = ToDocBlock.parse_md2docblock(formatted_md, mode=ToDocBlock.ONE_NOTE_MODE)

            new_page_element = PageElement(
                type=PageTypes.PAGE,
                id=self._md_file_list[file],
                children=id_list,
                name=title,
                created_at=metadata["created"],
                modified_at=metadata["updated"],
                export_name=self._export_path.name,
                export_id=self.export_id,
                relative_path=os.path.relpath(file, self._export_path),
            )

            for block in block_list:
                block.export_id = self.export_id

            required_resources = self._check_resources(block_list)

            yield new_page_element, block_list, required_resources

    def _check_resources(self, block_list: List[DocBlockElement]) -> List[Path]:
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
