import os

from pathlib import Path
from typing import Union, Any
from builtins import Exception

from .type_parsing import Md2DocBlock, NotMDFileError
from databasetools.managers.docs_manager import DocManager

class OneNoteTools:
    def __init__(
                self,
                db_uri: str,
                db_name: str,
                blocks_collection_name: str = "blocks",
                relations_collection_name: str = "relations"
            ):
        self.manager = DocManager(db_uri, db_name, blocks_collection_name, relations_collection_name)
        self.parser = Md2DocBlock(export_mode="generic")
        
    def upload_oneNote_export(self, dir_path: Union[Path, str]):
        items = [item for item in os.listdir(dir_path)]
        
        if len(items) != 2:
            raise NotOneNoteExport(f'Directory {dir_path} is not in the correct format. One note exports should only have two folders. Files found: {items}')
        
        for item in items:
            if item == "resources":
                self.store_resources(os.path.join(dir_path, "resources"))
            else:
                self.parser.set_export_mode("one_note")
                raw_path = os.path.join(dir_path, item)
                self.parser.set_home_dir(raw_path)
                missed_files = self.upload_dir(raw_path)
                self.parser.set_export_mode()
        
        return missed_files
    
    def store_resources(self, dir_path: Union[Path, str]):
        dir_path = Path(dir_path)
        
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(f"The specified directory path: {dir_path} does not exist.")
        
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            item_name, extension = os.path.splitext(item)
            
            with open(item_path, "rb") as f:
                self.manager.fs_store_file(f.read(), filename=item_name, extension=extension)
        
    def upload_dir(self, dir_path: Union[Path, str], depth: int = -1):
        if depth == 0:
            return
        
        dir_path = Path(dir_path)
        missed_files = []
        
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(f"The specified filepath: {dir_path} does not exist.")
        
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            
            if os.path.isdir(item_path):
                missed_files.extend(self.upload_dir(item_path, depth-1))
                continue
            
            try:
                self.upload_page(item_path)
            except NotMDFileError:
                missed_files.append(item_path)
            except Exception as e:
                raise Exception(f"From file {item_path}") from e
                
        return missed_files 
    
    def upload_page(self, file_path: Union[Path, Any]):
        try:
            block_elements = self.parser.process_page(file_path)
        except KeyError as e:
            raise Exception(f"Key Error at file: {file_path}") from e
        for block in block_elements:
            self.manager.upload_block(block)
            
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