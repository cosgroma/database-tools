""" This module contains the base controller class.

The base controller class is a generic controller that can be used to perform
CRUD operations on a MongoDB collection. It is used as a base class for
controllers that perform operations on specific collections.
"""

from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Type
from typing import TypeVar

from pydantic import BaseModel
from pymongo.collection import Collection

T = TypeVar("T", bound=BaseModel)


class GenericController(Generic[T]):
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

    def create(self, document_data: Dict[str, Any]) -> T:
        """
        Creates a new document in the collection.

        Parameters:
            document_data (Dict[str, Any]): The data of the document to create.

        Returns:
            T: The created document as a Pydantic model instance.
        """
        document = self.model(**document_data)
        self.collection.insert_one(document_data)
        return document

    # def create(self, document: T) -> T:
    #     """
    #     Creates a new document in the collection.

    #     Parameters:
    #         document (T): The document to create.

    #     Returns:
    #         T: The created document as a Pydantic model instance.
    #     """
    #     document_data = document.model_dump()
    #     self.collection.insert_one(document_data)
    #     return document

    def read(self, query: Dict[str, Any]) -> List[T]:
        """
        Reads documents from the collection.

        Parameters:
            query (Dict[str, Any]): The query to filter documents.

        Returns:
            List[T]: A list of document instances as Pydantic model objects.
        """
        documents = self.collection.find(query)
        return [self.model(**doc) for doc in documents]

    def update(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """
        Updates documents in the collection.

        Parameters:
            query (Dict[str, Any]): The query to filter documents to update.
            update_data (Dict[str, Any]): The data to update in the documents.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
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
