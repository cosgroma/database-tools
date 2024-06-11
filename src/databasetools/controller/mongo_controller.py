from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import json
from pydantic import ValidationError
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from .base_controller import DatabaseController
from .base_controller import T


class MongoCollectionController(DatabaseController[T]):
    """A generic controller that can be used to perform CRUD operations on a MongoDB collection.

    Attributes:
        collection (Collection): The MongoDB collection to perform operations on.
        model (Type[T]): The Pydantic model associated with the
            collection that represents the documents.

    Methods:
        create(document_data: Dict[str, Any]) -> T:
            Creates a new document in the collection.
        read(query: Dict[str, Any]) -> List[T]:
            Reads documents from the collection.
        update(query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
            Updates documents in the collection.
        delete(query: Dict[str, Any]) -> bool:
            Deletes documents from the collection.

    """

    def __init__(self, collection: Collection, model: Type[T]):
        """Initializes the generic controller.

        Parameters:
            collection (Collection): The MongoDB collection to perform operations on.
            model (Type[T]): The Pydantic model associated with the
                collection that represents the documents.
        """
        self.collection = collection
        self.model = model

    def create(self, item: Union[Dict[str, Any], T]) -> T:
        """
        Creates a new document in the collection.

        Parameters:
            item (Union[Dict[str, Any], T]): The document data to create.

        Returns:
            T: The created document as a Pydantic model instance.
        """
        try:
        
            if isinstance(item, dict):
                document = self.model(**item)
            elif isinstance(item, self.model):
                document = item
            else:
                raise ValueError(f"Item must be a dictionary or an instance of {self.model}")
            
            result = self.collection.insert_one(document.model_dump(by_alias=True))
            
            if not result.acknowledged:
                raise PyMongoError("Insert operation not acknowledged by MongoDB.")
            return document
        
        except ValidationError as e:
            # Handle validation errors
            print(f"Validation error: {e}")
            raise
        except PyMongoError as e:
            # Handle MongoDB errors
            print(f"Database error: {e}")
            raise

    def read(self, query: Dict[str, Any], limit: Optional[int] = None) -> List[T]:
        """
        Reads documents from the collection.

        Parameters:
            query (Dict[str, Any]): The query to filter documents.

        Returns:
            List[T]: A list of document instances as Pydantic model objects.
        """
        try:
            documents = self.collection.find(query).limit(limit) if limit else self.collection.find(query)
            return [self.model(**doc) for doc in documents]
        except ValidationError as e:
            raise ValidationError(f"Validation error: {e}") from e
        except PyMongoError as e:
            raise PyMongoError(f"Database error: {e}") from e
        except Exception as e:
            raise Exception(f"Error: {e}") from e

    def update(self, query: Dict[str, Any], update: Union[Dict[str, Any], T]) -> bool:
        """
        Updates documents in the collection.

        Parameters:
            query (Dict[str, Any]): The query to filter documents to update.
            update (Union[Dict[str, Any], T]): The update data.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if isinstance(update, dict):
            update_data = update
        elif isinstance(update, self.model):
            update_data = update.model_dump()
        result = self.collection.update_many(query, {"$set": update_data})
        return result.modified_count > 0

    def delete(self, query: Dict[str, Any]) -> bool:
        """
        Deletes documents from the collection.

        Parameters:
            query (Dict[str, Any]): The query to filter documents to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        result = self.collection.delete_many(query)
        return result.deleted_count > 0
    
    def delete_all(self):
        """
        Deletes all documents from the collection.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        result = self.collection.delete_many({})
        return result.deleted_count > 0
    
    def delete_item(self, item: Union[Dict[str, Any], T]) -> bool:
        """
        Deletes a single document from the collection.

        Parameters:
            item (Union[Dict[str, Any], T]): The document to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        if isinstance(item, dict):
            query = item
        elif isinstance(item, self.model):
            query = item.model_dump()
        else:
            raise ValueError("Item must be a dictionary or an instance of the model.")
        result = self.collection.delete_one(query)
        return result.deleted_count > 0

    def __iter__(self) -> "MongoCollectionController":
        """Returns an iterator object"""
        self._cursor = self.collection.find()
        return self

    def __next__(self) -> T:
        try:
            # Attempt to get the next document from the cursor
            document = next(self._cursor)
        except StopIteration:
            # If there are no more documents, raise StopIteration to stop the iteration
            raise StopIteration
        
        # Convert the document to a Pydantic model instance
        return self.model(**document)

    def __len__(self):
        return self.collection.count_documents({})

    def __repr__(self):
        return f"MongoCollectionController(collection={self.collection}, model={self.model})"
    
    def save_all_to_json(self, file_path: str) -> str:
        """
        Saves all documents in the collection to a JSON file.

        Parameters:
            file_path (str): The path to save the JSON file.
        """
        documents : List[T] = self.read({})
        json_array = [doc.model_dump() for doc in documents]
        with open(file_path, "w") as file:
            json.dump(json_array, file, indent=4)
        return file_path
