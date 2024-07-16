
import gridfs
import pymongo
from typing import Dict, Any, List
from pathlib import Path


from ..controller.mongo_controller import MongoCollectionController
from ..models.block_model import DocBlockElement, BlockRelationship


class DocManager:
    def __init__(
            self,
            db_uri: str,
            db_name: str,
            blocks_collection_name: str = "blocks",
            relations_collection_name: str = "relations",
            gridfs_name: str = "resources"
    ):
        self.db_uri = db_uri
        self.db_name = db_name
        self.blocks_collection_name = blocks_collection_name
        self.relations_collection_name = relations_collection_name
        self.gridfs_name = gridfs_name
        self.client = pymongo.MongoClient(db_uri)
        self.db = self.client[db_name]
        self.blocks_collection = self.db[blocks_collection_name]
        self.relations_collection = self.db[relations_collection_name]
        self.blocks_controller = MongoCollectionController(self.blocks_collection, DocBlockElement)
        self.relation_controller = MongoCollectionController(self.relations_collection, BlockRelationship)
        self.resources_db = self.client[gridfs_name]
        self.fs = gridfs.GridFS(self.resources_db)
        
    def fs_store_file(self, data: bytes, **kwargs):
        return self.fs.put(data, **kwargs)
    
    def fs_find_file(self, **kwargs):
        return self.fs.find_one(dict(kwargs))
    
    def reset_resources(self):
        self.client.drop_database(self.gridfs_name)
        self.resources_db = self.client[self.gridfs_name]
        self.fs = gridfs.GridFS(self.resources_db)
        
    def reset_collection(self): # Danger zone! For testing only!
        self.blocks_controller.delete_all()
    
    def upload_relation(self, relation: BlockRelationship):
        return self.relation_controller.create(relation)

    def upload_block(self, block: DocBlockElement):
        try:
            return self.blocks_controller.create(block)
        except Exception as e:
            raise Exception(f"Trying to add block: {block}") from e
    
    def update_block(self, block: DocBlockElement):
        return self.blocks_controller.update({"element_id": block.id}, block)
    
    def sync_block(self, block: DocBlockElement):
        update_result = self.update_block(block)
        if update_result:
            return block
        return self.upload_block(block)
    
    def upload_document(self, file_path: Path):
        '''
        1. Blockify document into relations and block
        2. Upload blocks and relations to respective collections
        '''
        
        pass

    def update_document(self, file_path: Path):
        '''
        1. Determine a query method for matching files to documents in mongo
        '''
        pass
    
    def find_blocks(self, **kwargs):
        return self.blocks_controller.read(dict(kwargs))

