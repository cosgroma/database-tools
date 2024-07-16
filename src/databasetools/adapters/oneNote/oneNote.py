import os
import frontmatter

from pathlib import Path
from typing import Optional, Union, Any, List
from builtins import Exception


from .md2docBlock import Md2DocBlock
from databasetools.managers.docs_manager import DocManager
from databasetools.models.block_model import DocBlockElement, DocBlockElementType

class OneNoteTools:
    def __init__(
                self,
                db_uri: str,
                db_name: str,
                blocks_collection_name: str = "blocks",
                relations_collection_name: str = "relations",
                gridfs_name: str = "resources",
                additional_trim_tokens: List[str] = None
            ):
        self.manager = DocManager(db_uri, db_name, blocks_collection_name, relations_collection_name, gridfs_name)
        self.parser = Md2DocBlock(ignore_token_type_list=additional_trim_tokens, mode_set=Md2DocBlock.ONE_NOTE_MODE)
        self.__current_dir_name = None
        self.__current_dir_path = None
        
    @property
    def _current_dir_name(self):
        return self.__current_dir_name
    
    @_current_dir_name.setter
    def _current_dir_name(self, _):
        raise AttributeError("Attempted to set directory name when it should not be accessed")
        
    @property
    def _current_dir_path(self):
        return self.__current_dir_path
    
    @_current_dir_path.setter
    def _current_dir_path(self, dir_path: Union[Path, str]):
        if self._current_dir_path:
            raise AlreadyAttachedToDir(f"Already working on a directory: {self.__current_dir_path}")
        else:
            self.__current_dir_path = Path(dir_path)
            self.__current_dir_name = os.path.basename(self.__current_dir_path)
            
    @_current_dir_path.deleter
    def _current_dir_path(self):
        self.__current_dir_path = None
        self.__current_dir_name = None
        
    def upload_oneNote_export(self, dir_path: Union[Path, str]):
        items = [item for item in os.listdir(dir_path)]
        
        if len(items) != 2:
            raise NotOneNoteExport(f'Directory {dir_path} is not in the correct format. One note exports should only have two folders. Files found: {items}')
        
        for item in items:
            if item == "resources":
                self.store_resources(os.path.join(dir_path, "resources"))
            else:
                raw_path = os.path.join(dir_path, item)
                self._current_dir_path = raw_path
                missed_files = self.upload_md_dir(raw_path)
                del self._current_dir_path
        return missed_files
        
    def upload_md_dir(self, dir_path: Union[Path, str], depth: int = -1):
        '''
        Make this function declare global dirpath variables 
        make it clean stuff up
        have it upload with parse_page_from_file
        '''    
        if depth == 0:
            return
        
        dir_path = Path(dir_path)
        missed_files = []
        
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"The specified filepath: {dir_path} does not exist.")
        elif not os.path.isdir(dir_path):
            raise FileNotFoundError(f"File path provided is not a directory: {dir_path}")
        
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            
            if os.path.isdir(item_path):
                missed_files.extend(self.upload_md_dir(item_path, depth-1))
                continue
            
            try:
                block_list = self.parse_page_from_file(item_path)
                self.upload_block_list(block_list)
            except NotMDFileError:
                missed_files.append(item_path)
            except Exception as e:
                raise Exception(f"From file {item_path}") from e
                
        return missed_files 
    
    def upload_block_list(self, block_list: List[DocBlockElement]):
        for item in block_list:
            self.manager.upload_block(item)
    
    def parse_page_from_file(self, file_path: Union[Path, str]) -> List[DocBlockElement]: # kinda done
        file_path = Path(file_path)
        
        if os.path.isdir(file_path):
            raise TypeError(f"Path: {file_path}, points to a directory.")
        elif not os.path.exists(file_path):
            raise FileExistsError(f"File: {file_path}, does not exist!")
        elif not os.path.basename(file_path).endswith(".md"):
            raise NotMDFileError(f"File: {file_path}, does not end with .md!")
        
        with open(file_path, "r") as md_file:
            metadata, md = frontmatter.parse(md_file.read())
            
        block_list, id_list = self.parser.md2docblock(md)
        
        relative_path = None
        
        if self._current_dir_path:
            relative_path = os.path.relpath(file_path, self._current_dir_path)
            
        new_attrs = {
            "oneNote_page_id": metadata.get("id"),
            "oneNoteId": metadata.get("oneNoteId"),
            "oneNote_created_at": metadata.get("created"),
            "oneNote_modified_at": metadata.get("updated"),
            "oneNote_path": metadata.get("oneNotePath"),
            "export_name": self.__current_dir_name,
            "export_relative_path": relative_path
        }
        
        new_block = DocBlockElement(
            type=DocBlockElementType.PAGE,
            children=id_list,
            name=str(metadata.get("title")),
            block_attr=new_attrs
        )
        
        block_list.insert(0, new_block)
        return block_list
        
    def store_resources(self, dir_path: Union[Path, str]):
        dir_path = Path(dir_path)
        
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(f"The specified directory path: {dir_path} does not exist.")
        
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            item_name, extension = os.path.splitext(item)
            
            with open(item_path, "rb") as f:
                self.manager.fs_store_file(f.read(), filename=item_name, extension=extension)   
    
    def verify_references(self):
        missing_resource = []
        items = self.manager.find_blocks(type="resource_reference")
        for item in items:
            filename = item.block_attr["filename"]
            extension = item.block_attr["extension"]
            result = self.manager.fs_find_file(filename=filename, extension=extension)
            if result:
                item.status = "Verified"
            else:
                missing_resource.append(item)
        return missing_resource
        
    def get_resource(self, file_name: str, extension: str):
            grid_out = self.manager.fs_find_file(filename=file_name, extension=extension)
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