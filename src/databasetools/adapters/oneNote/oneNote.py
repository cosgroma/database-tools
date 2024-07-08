import os

from pathlib import Path
from typing import Union, Dict, Any, List


from databasetools.models.block_model import DocBlockElement, PageElement, BlockRelationship, PageRelationship
from .type_parsing import OneNote_Export_to_DocBlock
from databasetools.managers.docs_manager import DocManager

class OneNoteTools:
    def __init__(
                self,
                db_uri: str,
                db_name: str,
                blocks_collection_name: str = "blocks",
                relations_collection_name: str = "relations"
            ):
        self.parser = OneNote_Export_to_DocBlock()
        self.manager = DocManager(db_uri, db_name, blocks_collection_name, relations_collection_name)
        
    def upload_dir(self, dir_path: Union[Path, Any], depth: int = -1):
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
            
            try:
                self.upload_page(item_path)
            except TypeError:
                missed_files.append(item_path)
            except Exception as e:
                raise Exception(f"From file {item_path}") from e
                
        return missed_files
                
    
    def upload_page(self, file_path: Union[Path, Any]):
        try:
            block_elements = self.parser.process_oneNote_page(file_path)
        except KeyError as e:
            raise Exception(f"Key Error at file: {file_path}") from e
        for block in block_elements:
            self.manager.upload_block(block)
        
